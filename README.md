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
$ python3 dockerl.py --image <image name> --nvidia <0 or 1>
```

For example, to run an **ubuntu** container with GPU support:
```bash
$ python3 dockerl.py --image ubuntu --nvidia 1

To get a container terminal run:  docker exec -it 0b2b964b8b8f /bin/bash
To kill the container run:        docker kill 0b2b964b8b8f

```

License
-------
The code in this repository is released under an [MIT license](https://github.com/luiscarlosgph/docker-with-graphics/blob/main/LICENSE).
