#/bin/bash

DOCKER_ID=`docker ps | grep backend | awk {'print $1'}`

echo `docker exec -it $DOCKER_ID python3 manage.py createsuperuser`
echo `root`
echo `qweqweqwe123123`
echo `qweqweqwe123123`
