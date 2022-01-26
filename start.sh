#! /bin/sh

DATA=$1
TAG=tango

if [ $# -eq 2 ]; then
	if [ "$2" = "--build" ]; then
		# Build the docker container
		docker build -f docker_build/Dockerfile.dev -t $TAG .
	fi
fi


# Run the docker container. Add additional -v if
# you need to mount more volumes into the container
# Also, make sure to edit the ports to fix your needs.
docker run -d --gpus all -u $(id -u):$(id -g) -v $(pwd):/tf/main	\
	--user root -v $DATA:/tf/data		\
	-p 8888:8888 --name $TAG $TAG
