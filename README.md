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
https://www.linuxtechi.com/how-to-install-docker-desktop-on-ubuntu/
https://docs.docker.com/desktop/setup/install/linux/ubuntu/ \

Note: Do modify the required resources for docker containers using docker desktop: memory to 8GB and cpu cores to 4

Install kubectl 
```bash
sudo apt-get update -y
sudo apt update && sudo apt-get install -y curl 
sudo apt update && sudo apt install python3 python3-venv python3-pip


curl -LO "https://dl.k8s.io/release/$(curl -Ls https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
rm kubectl

kubectl version --client
```

Install minikube
```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && sudo install minikube-linux-amd64 /usr/local/bin/minikube 
minikube version
```

----

### 1. Clone this repository

```bash
git clone https://github.com/AmanSharma216/mysql-deb-kafka-s3.git
cd mysql-deb-kafka-s3
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 2. Deploy MySQL

Apply your Kubernetes manifests:

```bash
cd ../mysql-deployment/
minikube start --cni=bridge --driver=docker
./run.sh
kubectl get pods -n mysql-deployment
kubectl exec -it mysql-0 -n mysql-deployment -- mysql -uroot -pamans -e "CREATE DATABASE kafkaDB;"
kubectl port-forward pod/mysql-0 3307:3306 -n mysql-deployment
```
Forwarded the the pod to localhost:3307 \
Use ConfigMaps to inject environment variables for dynamic configuration and passwords. \
Default root password: amans

---

### 3. Start Kafka Container

```bash
cd ../kafka-setup/
docker compose up --watch
```

---

### 4. Start Debezium and KafkaConnect Container

```bash
cd ../debezium-connect/
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
echo "customers,products,orders" | python ../playground/data-injection-scripts/mysqlDummyDataInjector.py

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
cd ../spark/
./spark_setup.sh
```

#### Ways to use Spark:
1. Run this in host terminal:
```
# Without Logging
docker exec -it glue-spark bash -c "
/home/glue_user/spark/bin/spark-submit \
  --master local[*] \
  --name 'KafkaAvroConsumer' \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-avro_2.12:3.3.0 \
  --jars /home/glue_user/spark/jars/commons-pool2-2.11.1.jar \
  --driver-class-path /home/glue_user/spark/jars/commons-pool2-2.11.1.jar \
  /home/glue_user/workspace/jupyter_workspace/scripts/consumer.py"

# Without Logging
docker exec -it glue-spark bash -c "
/home/glue_user/spark/bin/spark-submit \
  --master local[*] \
  --name 'KafkaAvroConsumer' \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-avro_2.12:3.3.0 \
  --files /home/glue_user/workspace/jupyter_workspace/log4j.properties \
  --conf "spark.driver.extraJavaOptions=-Dlog4j.configuration=file:/home/glue_userworkspace/jupyter_workspace/log4j.properties" \
  --jars /home/glue_user/spark/jars/commons-pool2-2.11.1.jar \
  --driver-class-path /home/glue_user/spark/jars/commons-pool2-2.11.1.jar \
  /home/glue_user/workspace/jupyter_workspace/scripts/consumer.py"

```
2. Using Dev Containers: \
Add VS Code Extension: Dev Containers \
Attach glue-spark container to VS Code window via Dev Containers extension and open terminal

```
# Without Logging
spark-submit --master local[*] --name "KafkaAvroConsumer" --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-avro_2.12:3.3.0 --jars /home/glue_user/spark/jars/commons-pool2-2.11.1.jar --driver-class-path /home/glue_user/spark/jars/commons-pool2-2.11.1.jar /home/glue_user/workspace/jupyter_workspace/scripts/consumer.py

# With Logging Enabled
spark-submit \
  --master local[*] \
  --name "KafkaAvroConsumer" \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,org.apache.spark:spark-avro_2.12:3.3.0 \
  --jars /home/glue_user/spark/jars/commons-pool2-2.11.1.jar \
  --driver-class-path /home/glue_user/spark/jars/commons-pool2-2.11.1.jar \
  --files /home/glue_user/workspace/jupyter_workspace/log4j.properties \
  --conf "spark.driver.extraJavaOptions=-Dlog4j.configuration=file:/home/glue_userworkspace/jupyter_workspace/log4j.properties" \
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
