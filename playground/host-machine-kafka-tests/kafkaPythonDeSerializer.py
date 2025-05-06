from confluent_kafka import Consumer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

# Kafka Consumer config
consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'avro-consumer-group',
    'auto.offset.reset': 'earliest'
}
topic = "test.kafkaDB.customers"
# Schema Registry config
schema_registry_conf = {
    'url': 'http://localhost:8081/'  # change to your Schema Registry URL
}

# Initialize clients
consumer = Consumer(consumer_conf)
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# Use generic AvroDeserializer (schema is auto-fetched from Schema Registry)
avro_deserializer = AvroDeserializer(schema_registry_client)

# Subscribe to topic
consumer.subscribe([topic])

# Poll and decode messages
print("Consuming Avro messages...")
try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Consumer error: {}".format(msg.error()))
            continue

        # Deserialize Avro message
        decoded_value = avro_deserializer(msg.value(), SerializationContext(msg.topic(), MessageField.VALUE))
        print("Decoded message:", decoded_value)
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
