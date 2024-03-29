### Docker setup
Before you start, make sure you have [docker](https://www.docker.com/get-started) installed on your machine

The django port will be exposed at http://localhost:8000/

After you start docker, to check statusm go to http://localhost:8000/admin to see if you can pull up the admin panel
#### To start docker
`sh scripts/start_docker.sh`
#### To re-start docker/deploy code to running docker
`sh scripts/restart_docker.sh`
#### To reset your database content
Delete database/ directory then restart your docker
#### To execute command in docker
First find the docker name/id

`docker ps --filter "name=atfoc_web"`

Then: 

`docker exec -it <docker id or name> <your command>`

For example, you want to create a test user yourself to use the django admin panel:

`docker exec -it <docker id or name> python manage.py createsuperuser`

#### Run unit test
Unit test run automatically when deploy to docker. Use the following command if you want to run it on your own
`docker exec -it $(docker ps -a | grep atfoc_web | awk '{print $1}') pytest <directory of the module you want to test>`

#### Check Django log
`docker-compose logs`

> add -f flag if you want to tag along...
