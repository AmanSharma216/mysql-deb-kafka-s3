from confluent_kafka import Consumer, KafkaException, KafkaError

conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'my-group',
    'auto.offset.reset': 'earliest'
}

consumer = Consumer(conf)

def message_callback(msg):
    print(f"Received message: {msg.value().decode('utf-8')}")

consumer.subscribe(['my-topic'])

try:
    while True:
        msg = consumer.poll(1.0)  # Wait for message (timeout 1 sec)
        if msg is None:
            continue
        elif msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f"End of partition reached {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")
            else:
                raise KafkaException(msg.error())
        else:
            message_callback(msg)
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
