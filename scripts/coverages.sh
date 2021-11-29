docker exec -i $(docker ps -a | grep atfoc_web | awk '{print $1}') coverage run --branch -m pytest -vvv identity listing > /dev/null
echo '==================branch coverage=================='
docker exec -i $(docker ps -a | grep atfoc_web | awk '{print $1}') coverage report -m 
docker exec -i $(docker ps -a | grep atfoc_web | awk '{print $1}') coverage run -m pytest -vvv identity listing > /dev/null
echo '==================statement coverage=================='
docker exec -i $(docker ps -a | grep atfoc_web | awk '{print $1}') coverage report -m 
