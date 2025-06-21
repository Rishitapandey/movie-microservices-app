import pika,json

params = pika.URLParameters('amqps://succbtrx:hi3zcPAZDovFZAUUZ1X-lZbcC-vuW2S9@campbell.lmq.cloudamqp.com/succbtrx')
connection = pika.BlockingConnection(params)
channel = connection.channel()

channel.queue_declare(queue='main')  # Declare the queue to ensure it exists

def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='main', body=json.dumps(body), properties=properties)
