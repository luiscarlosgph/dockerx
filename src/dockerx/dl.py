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
        proc = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT)
        out, err = proc.communicate()
        return out

    @staticmethod
    def xhost_available():
        return bool(DockerLauncher.shell('which xhost').decode('utf-8')) 

    @staticmethod
    def touch(fpath):
        """@brief Creates en empty file if it does not exist already."""
        if not os.path.isfile(fpath):
            pathlib.Path(fpath).touch()

    @staticmethod
    def interfaces():
        """@returns a list of network interfaces."""
        return [iface for _, iface in socket.if_nameindex()]
    
    @staticmethod
    def interface_exists(ifname):
        """@returns True if the network adapter exists. Otherwise, False."""
        return True if ifname in DockerLauncher.interfaces() else False

    @staticmethod
    def get_ip_from_interface(ifname, linux_siocgifaddr=0x8915):
        """
        @param[in]  ifname  Network adaptar name, e.g. 'eth0' or 'docker0'.
        @returns the IP address of a given network adapter.
        """
        if not DockerLauncher.interface_exists(ifname):
            raise ValueError("""[ERROR] You are trying to find the IP of a 
                network adapter that does not exist.""")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ifname_pack = struct.pack('256s', ifname[:15].encode('utf-8'))
        ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), linux_siocgifaddr, 
                              ifname_pack)[20:24])
        s.close()
        return ip

    @staticmethod
    def get_ip_from_display():
        """
        @details IPv6 not supported.
        @returns the IP address from the DISPLAY environment variable.
        """
        ip = None

        # Regex patterns (ipv4: RFC 791, hostname: RFC 952)
        ipv4_pattern = '^(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[:]\d+$'
        # TODO: ipv6_pattern = 
        hostname_pattern = '^((([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])'
        hostname_pattern += '\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9]))'
        hostname_pattern += '[:]\d+$'

        # Match DISPLAY with all the patterns
        ipv4_match = re.match(ipv4_pattern, os.environ['DISPLAY'])
        hostname_match = re.match(hostname_pattern, os.environ['DISPLAY'])
        
        # Get IP address 
        if ipv4_match:
            ip = ipv4_match.group(1) 
        elif hostname_match:
            hostname = hostname_match.group(1)
            ip = socket.gethostbyname(hostname)
        
        return ip

    @staticmethod
    def get_port_from_display(base_port=6000):
        offset = DockerLauncher.get_port_offset_from_display()
        return base_port + offset if offset else None

    @staticmethod
    def get_port_offset_from_display():
        port_offset = None
        port_pattern = '^.*[:](\d+)(?:[.]\d+|)$'
        m = re.match(port_pattern, os.environ['DISPLAY'])
        if m:
            port_offset = int(m.group(1))
        return port_offset

    @staticmethod
    def get_x11_server_socket_type(unix_socket_dir='/tmp/.X11-unix'):
        """
        @returns 'unix' if the X11 server specified in the DISPLAY is using
                 unix sockets. 
                 'tcp' if the X11 server specified in the DISPLAY is using
                 TCP sockets.
        """
        result = None

        # Check if there is a TCP server listening
        ip = DockerLauncher.get_ip_from_display()
        port = DockerLauncher.get_port_from_display()
        if ip is None:
            ip = socket.gethostbyname('localhost')
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        location = (ip, port)
        someone_listening = sock.connect_ex(location) == 0
        sock.close()
        if someone_listening:
            result = 'tcp'
        else:
            # Check if there is a unix socket listening 
            offset = DockerLauncher.get_port_offset_from_display() 
            path = os.path.join(unix_socket_dir, 'X' + str(offset))
            if pathlib.Path(path).exists():
                result = 'unix' 

        return result

    @staticmethod
    def prepare_environment(ifname, nvidia_runtime, additional_volumes, 
            additional_env_vars):
        """
        @brief Prepares the environment to launch a container with X11 
               support.
        @returns the dictionary of docker options.
        """
        # Initialise environment and volumes
        env = {'QT_X11_NO_MITSHM': 1}
        vol = {}

        # Detect whether the server is listening on TCP or UNIX sockets
        socket_type = DockerLauncher.get_x11_server_socket_type()

        # Prepare the Docker environment according to the type of X server
        if socket_type == 'unix':
            env['DISPLAY'] = os.environ['DISPLAY']
            vol['/tmp/.X11-unix'] = {'bind': '/tmp/.X11-unix', 'mode': 'rw'}
            if DockerLauncher.xhost_available():
                DockerLauncher.shell('xhost +SI:localuser:root')
        elif socket_type == 'tcp':
            # Discover the IP of the server
            if ifname is not None:
                if DockerLauncher.interface_exists(ifname):
                    ip = DockerLauncher.get_ip_from_interface(ifname) 
                else:
                    msg = """[WARN] dockerx: the network interface provided
                             to the DockerLauncher => """
                    msg += ifname
                    msg += """ <= could not be found in this computer.
                              Therefore, the IP address of the X server will
                              be retrieved from the existing DISPLAY 
                              environment variable. Make sure that you have it
                              properly set, i.e. pointing to the X server that
                              you want to use to display your GUIs.""" 
                    warnings.warn(msg)
                    ip = DockerLauncher.get_ip_from_display()
            else:
                ip = DockerLauncher.get_ip_from_display()
            
            # Get the port offset from the DISPLAY variable
            port_offset = DockerLauncher.get_port_offset_from_display()
            
            # Set DISPLAY for Docker container
            env['DISPLAY'] = ip + ':' + str(port_offset)

            # Create an empty Xauthority file if it does not exist
            env['XAUTHORITY'] = os.path.join(tempfile.gettempdir(), 
                '.docker.xauth')
            DockerLauncher.touch(env['XAUTHORITY'])

            # Hack X11 cookie
            out = DockerLauncher.shell('xauth nlist ' + os.environ['DISPLAY'])
            cookie = 'ffff' + out.decode('ascii')[4:]

            # Save X11 cookie in a temporary file
            cookie_path = os.path.join(tempfile.gettempdir(), '.myx11cookie')
            with open(cookie_path, 'w') as f:
                f.write(cookie)

            # Merge cookie in Xauthority file
            DockerLauncher.shell('xauth -f ' + env['XAUTHORITY'] \
                + ' nmerge ' + cookie_path)

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

    def launch_container(self, image_name, ifname='docker0',
            nvidia_runtime=False, volumes={}, env_vars={}, command=None):
        """
        @brief Launch a Docker container.
        
        @details The 'ifname' parameter is provided so that we can discover
                 the IP address of the adapter and pass it to the container 
                 in the DISPLAY variable. Of course, the IP of the adapter 
                 passed in 'ifname' must
                    1) be accessible from within the container you are 
                       launching
                    2) there must be an X11 server running on the IP
                       associated to the adapter
                 If you connect to a server via ssh using X11 forwarding 
                 (i.e. using 'ssh -X' or 'ForwardX11 yes' in your ssh config)
                 and you use the typical 'docker0' bridge adapter setup by 
                 docker by default, these two conditions are already met.

                 If you have a custom setup, either specify the ifname 
                 accordingly, or set it to None, and setup your DISPLAY
                 correctly pointing to your custom X11 server, but make sure
                 then that the IP in your DISPLAY is accessible from within 
                 the container you are launching.

        @param[in]  image_name      Name of the Docker image.
        @param[in]  ifname          Name of the Docker network adapter that
                                    will be attached to your container.
                                    The default value is 'docker0'.

                                    If you are sharing a different network 
                                    interface with the containers, 
                                    like 'docker1' or 'eth0', please specify 
                                    it.
                                    
                                    If an 'ifname' is provided, but the 
                                    network adapter does not exist, the IP of 
                                    the X11 server will be obtained from the 
                                    DISPLAY environment variable, and a 
                                    warning will be written to stderr. 
                                    This fallback option is designed
                                    to facilitate the use of this Python 
                                    module in different configurations.

                                    If you specify 'ifname=None' the IP of the
                                    X11 server will be inferred from your 
                                    DISPLAY environment variable. 

                                    If 'ifname=None' and there is no IP in 
                                    your DISPLAY, localhost will be assumed. 

        @param[in]  nvidia_runtime  Flag to enable the nvidia runtime, 
                                    default is False. 
        @param[in]  volumes         Dictionary of additional volumes you might
                                    want to add.
        @param[in]  env_vars        Dictionary of additional environment 
                                    variables you might want to add.
        @returns the Docker container object of the container launched.
        """
        # Prepare environment and volumes to run the container
        docker_options = DockerLauncher.prepare_environment(ifname, 
            nvidia_runtime, volumes, env_vars)

        # Launch container
        container = self.client.containers.run(image_name, detach=True,
            command=command, **docker_options)
        
        # Store it just in case we need it
        self.launched_containers.append(container)
        
        return container


if __name__ == '__main__':
    raise RuntimeError('[ERROR] This module is not meant to be run as a script.')
