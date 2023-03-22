Description
-----------

This repository contains a Python script that allows you to launch a docker 
container with X11 graphics support. 


Typical use case
----------------

A typical use case of this script is when you are connecting via ssh from your 
laptop to a remote computer (e.g. a DGX server) and you want to launch a docker 
container inside the remote computer with X11 support. 

A quick diagram:

Laptop => Remote computer (connected via ssh) => Docker container 

You want to launch a graphical application inside the Docker container and see the GUI in your laptop.


Requirements
------------

1. This package requires Python >= 3.9. Following [these](https://github.com/luiscarlosgph/how-to/tree/main/pyenv) instructions you can easily get any version of Python quickly up and running.

2. If you are launching this script on a server (e.g. DGX) you need to edit the 
configuration file of the SSH server, which is ```/etc/ssh/sshd_config```, and
add the option:

   ``` X11UseLocalhost no ```

   To edit ```/etc/ssh/sshd_config``` you need superuser access. After editing 
   this file you need to run:

   ```bash
   $ sudo service ssh reload
   ```

   This will reload the SSH server configuration without disconnecting existing 
   sessions. 

3. This package requires Python >= 3.9. If you do not know how to easily switch between Python versions, [here](https://github.com/luiscarlosgph/how-to/tree/main/pyenv) you have a tutorial on how to do it with **pyenv**.


Install using pip
-----------------

```bash
$ python3 -m pip install dockerx --user
```


Install this package from source
--------------------------------

```bash
$ sudo apt install python3 python3-pip
$ python3 -m pip install docker argparse --user
$ git clone https://github.com/luiscarlosgph/dockerx.git
$ cd dockerx
$ python3 setup.py install --user
```


Launch containers from your terminal
------------------------------------

To launch a container and execute a specific command inside the container:
```bash
$ python3 -m dockerx.run --name <container_name> --image <image_name> --nvidia <0_or_1> --command <command> --env <key=value> --volume <src>:<dst>
```
Options:
   * `--name`: name that you want to give to the container.
   * `--image`: name of the Docker image you want to deploy as a container.
   * `--nvidia`: flag to activate the NVIDIA runtime, necessary to run CUDA applications. Requires `nvidia-docker2`, if you do not have it installed, check [this](https://github.com/luiscarlosgph/how-to/tree/main/docker) link.
   * `--command`: use this parameter to launch jobs inside the 
container that require graphical (i.e. X11) support. The syntax is `--command <path_to_program_in_container> <parameters>`. As this package is meant to run graphical applications, no terminal output will be shown. If ```--command``` is not specified, the default command executed inside the container is that 
defined by the `CMD` keyword in the Dockerfile of your image. If None is defined (as happens for 
many images such as ```ubuntu``` or ```nvidia/cuda:11.7.1-base-ubuntu20.04```), the container will start, 
do nothing, and stop immediately. 
   * `--env`: flag used to define an environment variable that will be accessible from within the deployed container. You can define as many of them as you want. The syntax is `--env <key=value>`, e.g. `--env DISPLAY=:0 --env PATH=/usr/bin`.
   * `--volume`: flag used to mount a volume within the container, it can be a Docker volume or a folder from the host computer, the syntax is the same for both. You can define as many of them as you want. The syntax is `--volume <src>:<dst>`, e.g. `--volume /tmp/host_folder:/tmp/container_folder --volume /media/usb0:/mnt/usb0` (obviously, for this to work, the source folders must exist in the host computer). The source can also be an existing Docker volume, e.g. you create a volume with `docker volume create hello` and then mount it inside the container with `--volume hello:/tmp/hello`.
   * `--network`: use this option to specify the network that you want your container to connect to. If this option is not specified, the container is connected to the default Docker network.

Exemplary command to launch a container and run `PyCharm` from within the container:
```
$ python3 -m dockerx.run --name wild_turin --image luiscarlosgph/pycharm:latest --nvidia 1 --command /home/docker/pycharm/bin/pycharm.sh
```
This should display ```PyCharm``` in your screen.

**If you want to run multiple commands**, for example to install a graphical application and then run it, you can do it like this:
```
$ python3 -m dockerx.run --image nvidia/cuda:11.7.1-base-ubuntu20.04 --nvidia 1 --command '/bin/bash -c "apt update && apt install -y x11-apps && xclock"'
```
This should display ```xclock``` in your screen.

**If you want to run a container forever** so you can 1) bash into it with ```docker exec -it <container id> /bin/bash```
and 2) run GUIs inside the container, you can use `sleep infinity` as your command:
```bash
$ python3 -m dockerx.run --image <image name> --nvidia <0 or 1> --command 'sleep infinity'
```

For example, to run just an ```ubuntu``` container:
```bash
$ python3 -m dockerx.run --image ubuntu --command 'sleep infinity'

To get a container terminal run:  docker exec -it b05bd722477e /bin/bash
To kill the container run:        docker kill b05bd722477e
To remove the container run:      docker rm b05bd722477e

$ docker exec -it b05bd722477e /bin/bash
root@b05bd722477e:/# apt update && apt install -y x11-apps
root@b05bd722477e:/# xclock
```
After running ```xclock``` above you should see a clock in your local screen.

To run an ```ubuntu``` container **with CUDA support**:

```bash
$ python3 -m dockerx.run --image nvidia/cuda:11.7.1-base-ubuntu20.04 --nvidia 1 --command 'sleep infinity'

To get a container terminal run:  docker exec -it 0b2b964b8b8f /bin/bash
To kill the container run:        docker kill 0b2b964b8b8f
To remove the container run:      docker rm 0b2b964b8b8f

$ docker exec -it 0b2b964b8b8f /bin/bash
root@0b2b964b8b8f:/# nvidia-smi
Tue Sep 27 11:12:56 2022
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 515.65.01    Driver Version: 515.65.01    CUDA Version: 11.7     |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|                               |                      |               MIG M. |
|===============================+======================+======================|
|   0  NVIDIA TITAN X ...  Off  | 00000000:01:00.0  On |                  N/A |
| 23%   35C    P8    17W / 250W |    369MiB / 12288MiB |      0%      Default |
|                               |                      |                  N/A |
+-------------------------------+----------------------+----------------------+
                                                                               
+-----------------------------------------------------------------------------+
| Processes:                                                                  |
|  GPU   GI   CI        PID   Type   Process name                  GPU Memory |
|        ID   ID                                                   Usage      |
|=============================================================================|
+-----------------------------------------------------------------------------+
root@0b2b964b8b8f:/# apt update && apt install -y x11-apps
root@0b2b964b8b8f:/# xclock
```

As in the example above, ```xclock``` should be now shown in your local display.
However, this container has CUDA support. GPU applications can now be executed
and displayed from within the container.


Launch containers from your Python code
---------------------------------------

Exemplary code snippet that shows different ways to launch containers using the 
Python module in this repo. 

```python
import dockerx

dl = dockerx.DockerLauncher()

# If no command is specified here, the CMD in your Dockerfile will be executed, if there is no CMD in your 
# Dockerfile either, then this container will be created and immediately destroyed
container_0 = dl.launch_container('ubuntu')
print(container_0.id)

# If a command is specified here, the CMD in your Dockerfile will be ignored and overridden by the command 
# specified here
container_1 = dl.launch_container('ubuntu', command='sleep infinity')
print(container_1.id)

# Launch a container with CUDA support (as a command is specified, the CMD in your Dockerfile will be ignored)
container_2 = dl.launch_container('nvidia/cuda:11.7.1-base-ubuntu20.04', command='sleep infinity', nvidia_runtime=True)
print(container_2.id)
```


Run unit tests
--------------

```bash
$ python3 tests/test_docker_launcher.py
```


Author
------

Luis Carlos Garcia-Peraza Herrera (luiscarlos.gph@gmail.com).


License
-------

The code in this repository is released under an [MIT license](https://github.com/luiscarlosgph/docker-with-graphics/blob/main/LICENSE).
