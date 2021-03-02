Description
-----------
This repository contains a Python script that allows you to launch a docker container with X11 graphics support. 

Typical use case
----------------
A typical use case of this script is when you are connecting via ssh from your laptop to a remote computer (e.g. a DGX server)
and you want to launch a docker container inside the remote computer with X11 support. A quick diagram:

Laptop => Remote computer (connected via ssh) => Docker container 

You want to launch a graphical application inside the Docker container and see the GUI in your laptop.
   
Requirements
------------
If you are launching this script on a server (e.g. DGX) you need to edit the configuration file of the SSH server -> ```/etc/ssh/sshd_config``` and
add the option:

``` X11UseLocalhost no ```

To edit ```/etc/ssh/sshd_config``` you need superuser access. After editing this file you need to run:
```bash
$ sudo service ssh reload
```
This will reload the SSH server configuration without disconnecting existing sessions. 

Install dependencies
--------------------
```bash
$ sudo apt install python3 python3-pip
$ python3 -m pip install docker argparse --user
```

Install this package
--------------------
```bash
$ git clone https://github.com/luiscarlosgph/docker-with-graphics.git
$ cd docker-with-graphics
$ python3 setup.py install --user
```

Launch containers
-----------------
```bash
$ python3 -m dockerl.run --image <image name> --nvidia <0 or 1>
```

For example, to run just an **ubuntu** container:
```bash
$ python3 -m dockerl.run --image ubuntu

To get a container terminal run:  docker exec -it b05bd722477e /bin/bash
To kill the container run:        docker kill b05bd722477e

$ docker exec -it b05bd722477e /bin/bash
root@b05bd722477e:/# apt update && apt install -y x11-apps
root@b05bd722477e:/# xclock
```
After running ```xclock``` above you should see a clock in your laptop screen.

To run an **ubuntu** container **with CUDA support**:
```bash
$ python3 -m dockerl.run --image nvidia/cuda:11.0-base --nvidia 1

To get a container terminal run:  docker exec -it 0b2b964b8b8f /bin/bash
To kill the container run:        docker kill 0b2b964b8b8f

$ docker exec -it 0b2b964b8b8f /bin/bash
root@0b2b964b8b8f:/# apt update && apt install -y x11-apps
root@0b2b964b8b8f:/# xclock
```
As above, a clock should be shown in your display.

Launch containers from your Python code using this module:
----------------------------------------------------------
Exemplary code snippet that launches several containers, the last one with CUDA support. Remember that if no
CMD is specified in the Dockerfile, the container will be created and subsequently
destroyed. To keep the container running simply run ```sleep infinity``` as in the ```container_1``` example below.

```python
import dockerl

dl = dockerl.DockerLauncher()

# Launch a container with Ubuntu (as no command is specified, the CMD in your Dockerfile will be executed)
container_0 = dl.launch_container('ubuntu')
print(container_0.id)

# Launch a container with Ubuntu (as a command is specified, the CMD in your Dockerfile will be ignored)
container_1 = dl.launch_container('ubuntu', command='sleep infinity')
print(container_1.id)

# Launch a container with CUDA support (as a command is specified, the CMD in your Dockerfile will be ignored)
container_2 = dl.launch_container('nvidia/cuda:11.0-base', command='nvidia-smi', nvidia_runtime=True)
print(container_2.id)
```

License
-------
The code in this repository is released under an [MIT license](https://github.com/luiscarlosgph/docker-with-graphics/blob/main/LICENSE).
