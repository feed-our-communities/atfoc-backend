docker-compose up -d
docker ps
docker exec -i $(docker ps -a | grep atfoc_web | awk '{print $1}') pytest identity
docker exec -i $(docker ps -a | grep atfoc_web | awk '{print $1}') pytest listing
