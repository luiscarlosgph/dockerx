Description
-----------
This repository contains a Python script that allows you to launch a docker container with X11 graphics support. 

Typical use case
----------------
A typical use case of this script is when you are connecting via ssh from your laptop to a server (e.g. a DGX)
and you want to launch a docker container inside the server with X11 support. That is, you want to be able
to launch graphical applications inside the container and see the output in your laptop. 

How to use it
-------------
```bash
$ python3 launch_container.py --image-name <image name>
The container id is <container id>, to get a container terminal run: docker exec -it <container id> /bin/bash
```

For example, to run an **ubuntu** container:
```bash
$ python3 launch_container.py --image-name ubuntu
The container id is <container name>, to get a container terminal run: docker exec -it <container name> /bin/bash
```

If you are using the **nvidia runtime** because you are executing GPU applications inside the container, you can launch your container running:
```bash
$ python3 launch_container.py --image-name ubuntu --nvidia-runtime 1
The container id is <container name>, to get a container terminal run: docker exec -it <container name> /bin/bash
```

License
-------
The code in this repository is released under an [MIT license](https://github.com/luiscarlosgph/docker-with-graphics/blob/main/LICENSE).
