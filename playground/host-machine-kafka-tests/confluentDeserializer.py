from kafka import KafkaConsumer
import requests
from io import BytesIO
import json
from fastavro import schemaless_reader
# Kafka server details
bootstrap_servers = 'localhost:9092'  # Kafka server
topic = 'test.kafkaDB.customers'  # Kafka topic name
group_id = 'kpgroup4'  # Consumer group ID
schema_registry_url = 'http://localhost:8081'  # Schema registry URL

# Fetch schema from registry
def get_schema(schema_id):
    url = f"{schema_registry_url}/schemas/ids/{schema_id}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["schema"]

# Initialize Kafka consumer
consumer = KafkaConsumer(
    topic,
    bootstrap_servers=bootstrap_servers,
    group_id=group_id,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: x
)

# Consume and decode messages
for message in consumer:
    value_bytes = message.value
    print(f"Received message with raw bytes: {value_bytes[:10]}...")

    if value_bytes[0] != 0:
        print("Unknown magic byte, not Confluent Avro format")
        continue

    # Extract schema ID
    schema_id = int.from_bytes(value_bytes[1:5], byteorder='big')
    print(f"Schema ID from message: {schema_id}")

    # Fetch and parse schema
    raw_schema = get_schema(schema_id)
    parsed_schema = json.loads(raw_schema)  # safe JSON parsing

    # Deserialize message
    payload = BytesIO(value_bytes[5:])
    try:
        record = schemaless_reader(payload, parsed_schema)
        print(f"Decoded record: {record}")
    except Exception as e:
        print(f"Error decoding Avro message: {e}")
