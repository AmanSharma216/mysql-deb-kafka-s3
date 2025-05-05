# Real-Time Data Pipeline with Kafka, Debezium, MySQL, Kubernetes, and Spark

This project sets up a real-time data streaming architecture using Kafka, Debezium, MySQL, and Spark within a Kubernetes and Docker-based environment. It enables capturing MySQL changes and processing them in Spark for downstream analytics.

---

## ✨ Components

* **MySQL** – Source database for CDC (Change Data Capture)
* **Debezium** – CDC connector to stream MySQL changes into Kafka
* **Apache Kafka** – Message broker to handle event streaming
* **Apache Spark** – Stream processing engine (Structured Streaming)
* **Kubernetes** – Container orchestration
* **Docker & Docker Compose** – Containerized development environment

---

## 🛠 Requirements

* Docker
* Docker Compose
* Kubernetes (Minikube, k3s, or any cloud-managed cluster)
* kubectl
* Spark (Databricks, AWS GLUE or local cluster)

---

## 🧱 Architecture Overview

```
MySQL (binlog)
   │
Debezium (Connector)
   │
Kafka (topic: topic_prefix.kafkaDB.users)
   │
Spark Structured Streaming
   │
Delta Lake (Storage or Sink)
```

---

## 📦 Setup Instructions

### 1. Clone this repository

```bash
git clone https://github.com/your-org/kafka-debezium-pipeline.git
cd kafka-debezium-pipeline
```

### 2. Environment Configuration

Create a `.env` file:

```env
EXTERNAL_HOST=your.public.hostname.com
EXTERNAL_PORT=9091
```

These variables are used in your Kafka Docker Compose or Kubernetes ConfigMap.

---

### 3. Start Kafka, Zookeeper, and Debezium with Docker Compose

```bash
docker-compose up -d
```

Ensure your `docker-compose.yml` file uses `${EXTERNAL_HOST}:${EXTERNAL_PORT}` like so:

```yaml
KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://broker:29092,EXTERNAL://${EXTERNAL_HOST}:${EXTERNAL_PORT}
```

---

### 4. Deploy MySQL and Debezium on Kubernetes

Apply your Kubernetes manifests:

```bash
kubectl apply -f k8s/mysql-deployment.yaml
kubectl apply -f k8s/debezium-connector.yaml
```

Use ConfigMaps to inject environment variables for dynamic configuration.

---

### 5. Debezium Initial Snapshot

Debezium performs an initial snapshot by reading all current rows in MySQL tables. This snapshot is emitted to Kafka topics before streaming binlog events.

To enable snapshot:

```json
"snapshot.mode": "initial"
```

Debezium may emit `delete` events with `payload.after = null`.

---

### 6. Spark Structured Streaming

```python
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "broker:29092") \
    .option("subscribe", "topic_prefix.kafkaDB.users") \
    .option("startingOffsets", "earliest") \
    .option("group.id", "my-group") \
    .load()

kafka_df.writeStream \
    .format("delta") \
    .option("checkpointLocation", checkpoint_dir) \
    .trigger(availableNow=True) \
    .start(output_dir) \
    .awaitTermination()
```

---

## ✅ Debugging Tips

* Use `kcat` to verify Kafka messages:

  ```bash
  kcat -b ${EXTERNAL_HOST}:${EXTERNAL_PORT} -t topic_prefix.kafkaDB.users -C
  ```

* If you get API version issues, disable them:

  ```bash
  kcat -X api.version.request=false ...
  ```

* Verify metadata with:

  ```bash
  kcat -b ${EXTERNAL_HOST}:${EXTERNAL_PORT} -L
  ```

---

## 📋 Useful Notes

* Kafka topics may require `api.version.request=false` due to version mismatches.
* Use port tunneling with Serveo/Pinggy to expose Kafka externally.
* Debezium sends tombstone messages (null payload) for deletes – handle these in Spark if necessary.

---

## 📁 File Structure

```
.
├── docker-compose.yml
├── .env
├── k8s/
│   ├── mysql-deployment.yaml
│   ├── debezium-connector.yaml
│   ├── configmap.yaml
├── spark/
│   └── spark_streaming_job.py
└── README.md
```

---

## 🔺 Conclusion

This pipeline offers a robust CDC-based real-time architecture using open-source technologies. It's ideal for real-time analytics, auditing, and replicating MySQL changes efficiently.
