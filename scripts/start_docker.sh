docker-compose up -d
docker ps
sleep 5
docker exec -i $(docker ps -a | grep atfoc_web | awk '{print $1}') pytest -vvv identity listing
