import pyspark.sql.functions as func
from pyspark.sql import SparkSession
from confluent_kafka.schema_registry import SchemaRegistryClient          
from pyspark.sql.avro.functions import from_avro
import os

def get_schema_from_schema_registry(schema_registry_url, schema_registry_subject):
    sr = SchemaRegistryClient({'url': schema_registry_url})
    latest_version = sr.get_latest_version(schema_registry_subject)
    return sr, latest_version

JOB_NAME = "INGESTION"
kafka_url = "broker:29092"
schema_registry_url = "http://schema-registry:8081/"
kafka_producer_topic = "test.kafkaDB.customers"
schema_registry_subject = f"{kafka_producer_topic}-value"


spark = SparkSession.builder.appName("wikimedia_consumer") \
.getOrCreate()
spark.sparkContext.setLogLevel("ERROR")


wikimedia_df = spark \
.readStream\
.format("kafka")\
.option("kafka.bootstrap.servers", kafka_url)\
.option("subscribe", kafka_producer_topic)\
.option("startingOffsets", "earliest")\
.option("failOnDataLoss", "true")\
.load()



wikimedia_df = wikimedia_df.withColumn("magicByte", func.expr("substring(value, 1, 1)"))

wikimedia_df = wikimedia_df.withColumn("valueSchemaId", func.expr("substring(value, 2, 4)"))

wikimedia_df = wikimedia_df.withColumn("fixedValue", func.expr("substring(value, 6, length(value)-5)"))

wikimedia_value_df = wikimedia_df.select("magicByte", "valueSchemaId", "fixedValue")



_, latest_version_wikimedia = get_schema_from_schema_registry(schema_registry_url, schema_registry_subject)

fromAvroOptions = {"mode":"PERMISSIVE"}
decoded_output = wikimedia_df.select(
    from_avro(
        func.col("fixedValue"), latest_version_wikimedia.schema.schema_str, fromAvroOptions
    )
    .alias("wikimedia")
)
wikimedia_value_df = decoded_output.select("wikimedia.*")
wikimedia_value_df.printSchema()
wikimedia_value_df = wikimedia_value_df.select('before','after')

before_fields = wikimedia_value_df.schema["before"].dataType.fields
after_fields = wikimedia_value_df.schema["after"].dataType.fields

new_columns = (
    [func.col(f"before.{field.name}").alias(f"before.{field.name}") for field in before_fields] +
    [func.col(f"after.{field.name}").alias(f"after.{field.name}") for field in after_fields]
)

wikimedia_value_df = wikimedia_value_df.select(*new_columns)
wikimedia_value_df = wikimedia_value_df.withColumn("processing_time", func.current_timestamp())

checkpoint_dir = os.path.expanduser(f"/home/glue_user/workspace/jupyter_workspace/checkpoints/{JOB_NAME}/")
output_dir = os.path.expanduser(f"/home/glue_user/workspace/jupyter_workspace/data/{JOB_NAME}/")



wikimedia_value_df.writeStream \
.format("parquet") \
.outputMode("append") \
.option("truncate", "true") \
.option("checkpointLocation", checkpoint_dir) \
.start(output_dir) \
.awaitTermination(10)

spark.read.parquet(f"file:///{output_dir}").show()





