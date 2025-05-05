# pyspark imports
import pyspark.sql.functions as func
from pyspark.sql import SparkSession

kafka_url = "rnbwy-103-224-144-138.a.free.pinggy.link:41939"
schema_registry_url = "https://rnrbv-103-224-144-138.a.free.pinggy.link/"
kafka_producer_topic = "topic_prefix.kafkaDB.users"
schema_registry_subject = f"{kafka_producer_topic}-value"

# Create a SparkSession (the config bit is only for Windows!)
# .config("spark.jars", "/home/glue_user/workspace/system/commons-pool2-2.11.1.jar") \
# .config("spark.jars.packages", 
#             "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,"
#             "org.apache.spark:spark-avro_2.12:3.3.0") \
spark = SparkSession.builder.appName("wikimedia_consumer") \
.getOrCreate()
spark.sparkContext.setLogLevel("ERROR")


wikimedia_df = spark \
.readStream\
.format("kafka")\
.option("kafka.bootstrap.servers", kafka_url)\
.option("subscribe", kafka_producer_topic)\
.option("startingOffsets", "earliest")\
.option("failOnDataLoss", "false")\
.load()

# wikimedia_df.printSchema()

#  get magic byte value
wikimedia_df = wikimedia_df.withColumn("magicByte", func.expr("substring(value, 1, 1)"))

#  get schema id from value
wikimedia_df = wikimedia_df.withColumn("valueSchemaId", func.expr("substring(value, 2, 4)"))

# remove first 5 bytes from value
wikimedia_df = wikimedia_df.withColumn("fixedValue", func.expr("substring(value, 6, length(value)-5)"))

# creating a new df with magicBytes, valueSchemaId & fixedValue
wikimedia_value_df = wikimedia_df.select("magicByte", "valueSchemaId", "fixedValue")

from confluent_kafka.schema_registry import SchemaRegistryClient

def get_schema_from_schema_registry(schema_registry_url, schema_registry_subject):
    sr = SchemaRegistryClient({'url': schema_registry_url})
    latest_version = sr.get_latest_version(schema_registry_subject)

    return sr, latest_version


                  
from pyspark.sql.avro.functions import from_avro

# get schema using subject name
_, latest_version_wikimedia = get_schema_from_schema_registry(schema_registry_url, schema_registry_subject)

# deserialize data 
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



time = func.current_timestamp()
checkpoint_dir = f"/home/glue_user/workspace/system/checkpoints/test-cp-12/" 
wikimedia_value_df \
.writeStream \
.format("console") \
.outputMode("append") \
.option("truncate", "true") \
.option("checkpointLocation", checkpoint_dir) \
.start() \
.awaitTermination(10)




