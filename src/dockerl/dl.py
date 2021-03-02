##
# @brief  Launch a docker container with X11 support.
# @author Luis Carlos Garcia Peraza Herrera (luiscarlos.gph@gmail.com).
# @date   2 March 2021.

import subprocess
import shlex
import os
import tempfile
import re
import socket
import struct
import fcntl
import pathlib
import docker

class DockerLauncher:

    def __init__(self):
        self.client = docker.from_env()
        self.launched_containers = []

    @staticmethod
    def shell(cmd):
        """
        @brief Launches a terminal command and returns you the output.
        @param[in]  cmd  Command that you want to execute.
        """
        cmd_list = shlex.split(cmd, posix=False)
        proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, err = proc.communicate()
        return out

    @staticmethod
    def touch(fpath):
        """@brief Creates en empty file if it does not exist already."""
        if not os.path.isfile(fpath):
            pathlib.Path(fpath).touch()

    @staticmethod
    def get_ip(ifname, linux_siocgifaddr=0x8915):
        """@returns the IP address of a given network adapter."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ifname_pack = struct.pack('256s', ifname[:15].encode('utf-8'))
        return socket.inet_ntoa(fcntl.ioctl(s.fileno(), linux_siocgifaddr, ifname_pack)[20:24])

    @staticmethod
    def prepare_environment(ifname, nvidia_runtime, additional_volumes, additional_env_vars):
        """
        @brief Prepares the environment to launch a container with X11 support.
        @returns the dictionary of docker options.
        """
        # Initialise environment and volumes
        env = {'QT_X11_NO_MITSHM': 1}
        vol = {}
        
        # Detect whether there is a local X server
        local_x_server = re.match('^[:]\d+$', os.environ['DISPLAY'])    
        
        if local_x_server:  
            env['DISPLAY'] = os.environ['DISPLAY']
            vol['/tmp/.X11-unix'] = {'bind': '/tmp/.X11-unix', 'mode': 'rw'}
            DockerLauncher.shell('xhost +SI:localuser:root')
        else:  # e.g. we are in a remote machine via SSH with X11 forwarding enabled (ssh -X or -Y)
            # Set DISPLAY 
            ip = DockerLauncher.get_ip(ifname)
            port_offset = os.environ['DISPLAY'].split(':')[1]
            env['DISPLAY'] = ip + ':' + port_offset

            # Create an empty Xauthority file if it does not exist
            env['XAUTHORITY'] = os.path.join(tempfile.gettempdir(), '.docker.xauth')
            DockerLauncher.touch(env['XAUTHORITY'])

            # Hack X11 cookie
            out = DockerLauncher.shell('xauth nlist ' + os.environ['DISPLAY'])
            cookie = 'ffff' + out.decode('ascii')[4:]

            # Save X11 cookie in a temporary file
            cookie_path = os.path.join(tempfile.gettempdir(), '.myx11cookie')
            with open(cookie_path, 'w') as f:
                f.write(cookie)

            # Merge cookie in Xauthority file
            DockerLauncher.shell('xauth -f ' + env['XAUTHORITY'] + ' nmerge ' + cookie_path)

            # Mount Xauthority file inside the container
            vol[env['XAUTHORITY']] = {'bind': env['XAUTHORITY'], 'mode':"rw"}
        
        # Prepare dictionary of options for docker
        env.update(additional_env_vars)
        vol.update(additional_volumes)
        docker_options = {
            'environment' : env,
            'volumes' : vol,
        }
        if nvidia_runtime:
            docker_options['runtime'] = 'nvidia'
        
        return docker_options


    def launch_container(self, image_name, ifname='docker0', nvidia_runtime=False, volumes={}, 
            env_vars={}, command=None):
        """
        @brief Launch a Docker container.

        @param[in]  image_name      Name of the Docker image.
        @param[in]  ifname          Name of the virtual Docker network adapter, default is docker0.
        @param[in]  nvidia_runtime  Flag to enable the nvidia runtime, default is False. 
        @param[in]  volumes         Dictionary of additional volumes you might want to add.
        @param[in]  env_vars        Dictionary of additional environment variables you might want
                                    to add.
        @returns the Docker container object of the container launched.
        """
        # Prepare environment and volumes to run the container
        docker_options = DockerLauncher.prepare_environment(ifname, nvidia_runtime, volumes,
            env_vars)

        # Launch container
        container = self.client.containers.run(image_name, detach=True,
            command=command, **docker_options)
        
        # Store it just in case we need it
        self.launched_containers.append(container)
        
        return container


if __name__ == '__main__':
    raise RuntimeError('[ERROR] This module is not meant to be run as a script.')
