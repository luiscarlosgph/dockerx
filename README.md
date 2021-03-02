Description
-----------
This repository contains a Python script that allows you to launch a docker container with X11 graphics support. 

Typical use case
----------------
A typical use case of this script is when you are connecting via ssh from your laptop to a server (e.g. a DGX)
and you want to launch a docker container inside the server with X11 support. That is, you want to be able
to launch graphical applications inside the container and see the output in your laptop. 

Requirements
------------
If you are launching this script on a server (e.g. DGX) you need to edit the ```/etc/ssh/sshd_config``` file and
add the option: 

``` X11UseLocalhost no```

To edit ```/etc/ssh/sshd_config``` you need superuser access.

How to use it
-------------
```bash
$ python3 dockerl.py --image <image name> --nvidia <0 or 1>
```

For example, to run just an **ubuntu** container:
```bash
$ python3 dockerl.py --image ubuntu

To get a container terminal run:  docker exec -it b05bd722477e /bin/bash
To kill the container run:        docker kill b05bd722477e

$ docker exec -it b05bd722477e /bin/bash
root@b05bd722477e:/#
```

For example, to run an **ubuntu** container with CUDA support:
```bash
$ python3 dockerl.py --image nvidia/cuda:11.0-base --nvidia 1

To get a container terminal run:  docker exec -it 0b2b964b8b8f /bin/bash
To kill the container run:        docker kill 0b2b964b8b8f

$ docker exec -it 0b2b964b8b8f /bin/bash
root@0b2b964b8b8f:/#
```

License
-------
The code in this repository is released under an [MIT license](https://github.com/luiscarlosgph/docker-with-graphics/blob/main/LICENSE).
