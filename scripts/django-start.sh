#!/bin/sh
# wait-for-postgres.sh

while ! pg_isready -h atfoc_db_host ; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1.5
done
 
>&2 echo "Postgres is up - executing command"
# always install the requirements to make sure it is up to date
python -m pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
