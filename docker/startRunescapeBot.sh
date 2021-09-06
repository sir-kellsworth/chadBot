#!/bin/bash

loc=$(dirname "$(readlink -f "$0")")
pushd ${loc}

docker run -it --rm \
	--privileged \
	-v ${loc}/../python:/tmp/work/python \
	-v ${loc}/../config:/tmp/work/config \
	-v /etc/localtime:/etc/localtime:ro \
	-v ~/.config/pulse/cookie:/home/bigBoy/.config/pulse/cookie \
	-v /run/user/${USER_UID}/pulse/native:/run/user/1000/pulse/native \
	-v /tmp/.X11-unix:/tmp/.X11-unix \
	-v /dev/shm:/dev/shm \
	--env="DISPLAY" \
	--device /dev/dri \
	--device /dev/snd \
	--group-add audio \
	--name runescape \
	runescape

popd
