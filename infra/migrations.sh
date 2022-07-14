#/bin/bash

DOCKER_ID=`docker ps | grep backend | awk {'print $1'}`

echo `docker exec -it $DOCKER_ID python3 manage.py makemigrations`
echo `docker exec -it $DOCKER_ID python3 manage.py migrate`
echo `docker exec -it $DOCKER_ID python3 manage.py collectstatic --no-input`
echo `docker exec -it $DOCKER_ID python3 manage.py ingredients`
