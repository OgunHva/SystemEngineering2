# Create docker network bridge
```
docker network create -d bridge localnet --subnet=145.168.0.0/24 --gateway=145.168.0.1
```
### Hadoop web port
```
http://<IP OF NODE>:9870/


### Docker build
docker build -t dabbhadoop --build-arg SSH_PRIVATE_KEY="$(cat /home/hadoop/.ssh/id_rsa)"i --build-arg SSH_PUBLIC_KEY="$(cat /home/hadoop/.ssh/id_rsa.pub)" .
