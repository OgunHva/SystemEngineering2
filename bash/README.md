# Create docker network bridge
```
docker network create -d bridge localnet --subnet=145.168.0.0/24 --gateway=145.168.0.1
```
### Hadoop web port
```
http://<IP OF NODE>:9870/
