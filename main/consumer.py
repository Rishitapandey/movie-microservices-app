import pika, json
from main import Product, db, app

params = pika.URLParameters('amqps://succbtrx:hi3zcPAZDovFZAUUZ1X-lZbcC-vuW2S9@campbell.lmq.cloudamqp.com/succbtrx')
connection = pika.BlockingConnection(params)

channel = connection.channel()
channel.queue_declare(queue='main')

def callback(ch, method, properties, body):
    print('Received in main')
    try:
        data = json.loads(body)
        print(data)
        
        with app.app_context():
            if properties.content_type == 'product_created':
                product = Product(id=data['id'], title=data['title'], image=data['image'])
                db.session.add(product)
                db.session.commit()
                print('Product Created')

            elif properties.content_type == 'product_updated':
                product = Product.query.get(data['id'])
                if product:
                    product.title = data['title']
                    product.image = data['image']
                    db.session.commit()
                    print('Product Updated')
                else:
                    print(f"Product with ID {data['id']} not found for update")

            elif properties.content_type == 'product_deleted':
                # Ensure data contains the ID (could be just the ID or a dict with 'id')
                product_id = data if isinstance(data, int) else data.get('id')
                product = Product.query.get(product_id)
                if product:
                    db.session.delete(product)
                    db.session.commit()
                    print(f'Product {product_id} Deleted')
                else:
                    print(f"Product with ID {product_id} not found for deletion")

    except json.JSONDecodeError:
        print("Error: Invalid JSON received")
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        # Consider implementing dead-letter queue here

channel.basic_consume(queue='main', on_message_callback=callback, auto_ack=True)
print('Started Consuming')

try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("Stopping consumer...")
finally:
    channel.close()
    connection.close()