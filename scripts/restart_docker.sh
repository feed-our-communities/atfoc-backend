docker stop $(docker ps -a | grep atfoc_db | awk '{print $1}')
docker stop $(docker ps -a | grep atfoc_web | awk '{print $1}')
docker-compose up -d
docker ps
sleep 5
docker exec -i $(docker ps -a | grep atfoc_web | awk '{print $1}') pytest identity
docker exec -i $(docker ps -a | grep atfoc_web | awk '{print $1}') pytest listing
