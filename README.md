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

## 📁 File Structure
```
├── debezium-connect/
│   ├── docker-compose.yaml
│   ├── Dockerfile
│   └── Ingestion-deb-connector-config
├── kafka_setup/
│   └── docker-compose.yaml
├── mysql_deployment/
│   ├── mysql-secret.yaml
│   ├── mysql-configmap.yaml
│   ├── mysql-services.yaml
│   └── mysql-statefulset.yaml
├── playground/
│   ├── data-injection-scripts/
│   │   └── mysqlDummyDataInjector.py
│   └── host-machine-kafka-tests-secret/
│       ├── confluentDeserializer.py
│       └── kafkaPythonDeserializer.py
├── spark/
│   ├── checkpoints/
│   ├── data/
│   ├── scripts/
│   │   └── consumer.py
│   ├── log4j.properties
│   └── spark_setup.sh
├── README.md
├── .gitignore
└── requirements.txt
```

---


## 🧱 Architecture Overview

```
MySQL (binlog)
   │
Debezium (MySQL Connector)
   │
Kafka (topic: topic_prefix.kafkaDB.users)
   │
Spark Structured Streaming
   │
Delta Lake (Storage or Sink)
```

---

## 📦 Setup Instructions

### 0. Installations for Linux
Install docker and docker compose \
https://support.netfoundry.io/hc/en-us/articles/360057865692-Installing-Docker-and-docker-compose-for-Ubuntu-20-04

Install kubectl 
```bash
sudo apt-get update -y
sudo apt-get install -y curl

curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

kubectl version --client
```

Install minikube
```bash
sudo apt-get install -y conntrack

curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64

minikube version
```

----

### 1. Clone this repository

```bash
git clone https://github.com/AmanSharma216/mysql-deb-kafka-s3.git
cd mysql-deb-kafka-s3
```

---

### 2. Deploy MySQL

Apply your Kubernetes manifests:

```bash
cd ~/mysql-deb-kafka-s3/mysql-deployment/
minikube start --cni=bridge --driver=docker
./run.sh
kubectl get pods -n mysql-deployment
kubectl port-forward pod/mysql-0 3307:3306 -n mysql-deployment
```
Forwarded the the pod to localhost:3307 \
Use ConfigMaps to inject environment variables for dynamic configuration and passwords. \
Default root password: amans

---

### 3. Start Kafka Container

```bash
cd ~/mysql-deb-kafka-s3/kafka-setup/
docker compose up --watch
```

---

### 4. Start Debezium and KafkaConnect Container

```bash
cd ~/mysql-deb-kafka-s3/debezium-connect/
docker compose up --watch
```

---

### 5. Check urls in browser:

Kafdrop
http://localhost:9000

Kafka-connect-UI
http://localhost:8000

schema registry
http://localhost:8081/subjects

---

### 6. Create dummy tables to mysql deployment

```bash
pip install -r requirements.txt
python ~/mysql-deb-kafka-s3/playground/data-injection-scripts/mysqlDummyDataInjector.py
```

---


### 7. Create Debezium MySQL Connector


Visit the Debezium UI in your browser:

```
http://localhost:8000
```

> 🧭 Navigate to **Connectors → New Connector → MySQL Connector**.

In the configuration section, paste debezium-connect/Ingestion-deb-connector-config.txt

Click **Create**.

---

### 8. Check Kafka Topic via Kafdrop:



Visit the Kafdrop UI in your browser:

```
http://localhost:9000
```

---

### 9. Run PySpark Script for data ingestion

Creating spark enviroment
```bash
cd ~/mysql-deb-kafka-s3/spark/
./spark_setup.sh
```
Attach glue-spark container to VS Code window via Web Containers extension and open terminal

```
# Without Logging
spark-submit \
  --master local[*] \
  --name "KafkaAvroConsumer" \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-avro_2.12:3.3.0 \
  --jars /home/glue_user/spark/jars/commons-pool2-2.11.1.jar \
  --driver-class-path /home/glue_user/spark/jars/commons-pool2-2.11.1.jar \
  /home/glue_user/workspace/jupyter_workspace/scripts/consumer.py

# With Logging Enabled
spark-submit \
  --master local[*] \
  --name "KafkaAvroConsumer" \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-avro_2.12:3.3.0 \
  --jars /home/glue_user/spark/jars/commons-pool2-2.11.1.jar \
  --driver-class-path /home/glue_user/spark/jars/commons-pool2-2.11.1.jar \
  --files /home/glue_user/workspace/jupyter_workspace/log4j.properties \
  --conf "spark.driver.extraJavaOptions=-Dlog4j.configuration=file:/home/glue_user/workspace/jupyter_workspace/log4j.properties" \
  /home/glue_user/workspace/jupyter_workspace/scripts/consumer.py

```

---

## ✅ Debugging Tips

* Use `kcat` to verify Kafka messages inside host machine:

  ```bash
  kcat -b localhost:9092 -t cdc_connect_configs -C
  ```

* Verify metadata with:

  ```bash
  kcat -b localhost:9092 -t cdc_connect_configs -L
  ```

---

## 📋 Useful Notes

* Use port tunneling with Serveo/Pinggy to expose Kafka externally.
* Debezium sends tombstone messages (null payload) for deletes – handle these in Spark if necessary.

---

## 🔺 Conclusion

This pipeline offers a robust CDC-based real-time architecture using open-source technologies. It's ideal for real-time analytics, auditing, and replicating MySQL changes efficiently.
