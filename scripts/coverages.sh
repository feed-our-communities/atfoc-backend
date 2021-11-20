docker exec -i $(docker ps -a | grep atfoc_web | awk '{print $1}') coverage run --branch -m pytest -vvv identity listing
docker exec -i $(docker ps -a | grep atfoc_web | awk '{print $1}') coverage report -m 
docker exec -i $(docker ps -a | grep atfoc_web | awk '{print $1}') coverage run -m pytest -vvv identity listing
docker exec -i $(docker ps -a | grep atfoc_web | awk '{print $1}') coverage report -m 
