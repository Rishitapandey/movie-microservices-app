import pika, json

params = pika.URLParameters('amqps://succbtrx:hi3zcPAZDovFZAUUZ1X-lZbcC-vuW2S9@campbell.lmq.cloudamqp.com/succbtrx')

connection = pika.BlockingConnection(params)

channel = connection.channel()


def publish(method, body):
    properties = pika.BasicProperties(method)
    channel.basic_publish(exchange='', routing_key='admin', body=json.dumps(body), properties=properties)