docker stop $(docker ps -a | grep atfoc_db | awk '{print $1}')
docker stop $(docker ps -a | grep atfoc_web | awk '{print $1}')
