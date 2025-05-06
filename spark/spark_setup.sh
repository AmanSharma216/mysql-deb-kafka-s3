#!/bin/bash

# Check if Docker Desktop is running (since we're on Linux, we'll assume Docker is installed)
if ! docker ps > /dev/null 2>&1; then
    echo "Docker is not running. Attempting to start Docker..."

    # Check for Docker Desktop and start it
    if command -v systemctl > /dev/null && systemctl --user is-active docker-desktop > /dev/null 2>&1; then
        echo "Docker Desktop is already running."
    else
        echo "Starting Docker Desktop..."
        systemctl --user start docker-desktop
    fi

    # Wait for Docker to start
    until docker ps > /dev/null 2>&1; do
        echo "Waiting for Docker to start..."
        sleep 5
    done

    echo "Docker is running."
fi


echo "Docker is ready."

# Set up Docker container with specified volumes, environment variables, and ports
docker rm -f glue-spark
docker run -itd  -e DISABLE_SSL=true --rm \
    -p 4040:4040 -p 18080:18080 -p 8998:8998 -p 8888:8888 \
    -v "$(pwd)/spark":/home/glue_user/workspace/jupyter_workspace \
    --network kafka_setup_default \
    --name glue-spark amaneazydiner/aws-glue-libs:glue_libs_4.0.0_image_01\
    /home/glue_user/jupyter/jupyter_start.sh

# Wait for the container to start
sleep 3

docker exec -it --user root glue-spark /bin/bash -c "
    yum install -y sudo passwd &&
    echo 'root:root' | sudo chpasswd &&
    echo 'glue_user:glue_user' | sudo chpasswd &&
    cd /home/glue_user/spark/jars
    wget https://repository.mulesoft.org/nexus/content/repositories/public/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar 
    wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-j-9.0.0.tar.gz
    tar -xvzf mysql-connector-j-9.0.0.tar.gz
    find mysql-connector-j-9.0.0 -name "*.jar" -exec mv {} . \;
    rm -rf mysql-connector-j-9.0.0 mysql-connector-j-9.0.0.tar.gz
    cd /home/glue_user
    python3 --version
    pip3 install python-dotenv
    pip3 install confluent-kafka --no-build-isolation --prefer-binary
    sudo yum install -y gcc make librdkafka-devel yajl-devel
    git clone https://github.com/edenhill/kcat.git
    cd kcat
    ./configure
    make
    sudo make install
    echo 'Done'
"

sleep 10

