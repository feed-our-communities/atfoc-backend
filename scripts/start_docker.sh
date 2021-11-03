docker-compose up -d
docker ps
docker exec -it $(docker ps -a | grep atfoc_web | awk '{print $1}') pytest identity
