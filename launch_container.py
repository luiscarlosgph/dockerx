##
# @brief  Launch a docker container with X11 support.
# @author Luis Carlos Garcia Peraza Herrera (luiscarlos.gph@gmail.com).
# @date   2 March 2021.

import sys
import argparse
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

def shell(cmd):
    """
    @brief Launches a terminal command and returns you the output.
    @param[in]  cmd  Command that you want to execute.
    """
    cmd_list = shlex.split(cmd, posix=False)
    proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = proc.communicate()
    return out


def touch(fpath):
    """@brief Creates en empty file if it does not exist already."""
    if not os.path.isfile(fpath):
        pathlib.Path(fpath).touch()


def get_ip(ifname, linux_siocgifaddr=0x8915):
    """@returns the IP address of a given network adapter."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ifname_pack = struct.pack('256s', ifname[:15].encode('utf-8'))
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), linux_siocgifaddr, ifname_pack)[20:24])


def prep_docker_env(ifname='docker0', nvidia_runtime=False):
    """@returns the dictionary of docker options."""
    # Initialise environment and volumes
    env = {'QT_X11_NO_MITSHM': 1}
    vol = {}
    
    # Detect whether there is a local X server
    local_x_server = re.match('^[:]\d+$', os.environ['DISPLAY'])    
    
    if local_x_server:  
        env['DISPLAY'] = os.environ['DISPLAY']
        vol['/tmp/.X11-unix'] = {'bind': '/tmp/.X11-unix', 'mode': 'rw'}
        shell('xhost +SI:localuser:root')
    else:  # e.g. we are in a remote machine via SSH with X11 forwarding enabled (ssh -X or -Y)
        # Set DISPLAY 
        ip = get_ip(ifname)
        port_offset = os.environ['DISPLAY'].split(':')[1]
        env['DISPLAY'] = ip + ':' + port_offset

        # Create an empty Xauthority file if it does not exist
        env['XAUTHORITY'] = os.path.join(tempfile.gettempdir(), '.docker.xauth')
        touch(env['XAUTHORITY'])

        # Hack X11 cookie
        out = shell('xauth nlist ' + os.environ['DISPLAY'])
        cookie = 'ffff' + out.decode('ascii')[4:]

        # Save X11 cookie in a temporary file
        cookie_path = os.path.join(tempfile.gettempdir(), '.myx11cookie')
        with open(cookie_path, 'w') as f:
            f.write(cookie)

        # Merge cookie in Xauthority file
        shell('xauth -f ' + env['XAUTHORITY'] + ' nmerge ' + cookie_path)

        # Mount Xauthority file inside the container
        vol[env['XAUTHORITY']] = {'bind': env['XAUTHORITY'], 'mode':"rw"}
    
    # Prepare dictionary of options for docker
    docker_options = {
        'environment' : env,
        'volumes' : vol,
    }
    if nvidia_runtime:
        docker_options['runtime'] = 'nvidia'
    
    return docker_options


def parse_command_line_parameters(parser):
    parser.add_argument('--image', required=True, help='Docker image name.',)
    parser.add_argument('--nvidia', required=False, default=False, 
                        help='Activate the use of nvidia runtime. Default is 0.')
    args = parser.parse_args()
    args.nvidia = bool(int(args.nvidia))
    return args


def main():
    # Parse command line parameters
    parser = argparse.ArgumentParser()
    args = parse_command_line_parameters(parser)
    
    # Prepare environment and volumes to run the container
    docker_options = prep_docker_env(nvidia_runtime=args.nvidia)

    # Launch container
    container = docker.from_env().containers.run(args.image, detach=True,
        command=['sleep', 'infinity'], **docker_options)
    
    # Print info for the user
    sys.stdout.write("\nTo get a container terminal run:  ") 
    sys.stdout.write('docker exec -it ' + container.id[:12]  + " /bin/bash\n") 
    sys.stdout.write("To kill the container run:  ") 
    sys.stdout.write('      docker kill ' + container.id[:12] + "\n\n") 

if __name__ == '__main__':
    main()
