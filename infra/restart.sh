#/bin/bash
DOCKER_ID=`docker ps | grep backend | awk {'print $1'}`
DODCKER_IMG=`docker image list | grep backend | awk {'print $3'}`

echo `docker-compose down`
echo `docker rm -f $DOCKER_ID`
echo `docker rmi -f $DODCKER_IMG`
echo `docker-compose up`
echo `docker exec -it $DOCKER_ID python3 manage.py makemigrations`
echo `docker exec -it $DOCKER_ID python3 manage.py migrate`
