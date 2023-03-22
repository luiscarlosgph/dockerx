"""
@brief  Unit tests for the launcher of docker containers with X11 support.
@author Luis C. Garcia Peraza Herrera (luiscarlos.gph@gmail.com).
@date   15 April 2021 -> Happy birthday to my sister!
"""

import unittest
import os
import socket
import pathlib
import subprocess
import time

# My imports
import dockerx


def is_port_in_use(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    sock.close()
    return True if result == 0 else False
    

class TestDockerLauncher(unittest.TestCase):

    def test_get_ip_from_interface(self):
        ip = dockerx.DockerLauncher.get_ip_from_interface('lo')
        self.assertEqual(ip, '127.0.0.1')
    
    def test_get_ip_from_display(self):
        # Positive IP test
        os.environ['DISPLAY'] = '192.168.69.96:99'
        ip = dockerx.DockerLauncher.get_ip_from_display()
        self.assertEqual(ip, '192.168.69.96')

        # Positive hostname test
        os.environ['DISPLAY'] = 'localhost:23'
        ip = dockerx.DockerLauncher.get_ip_from_display()
        self.assertEqual(ip, '127.0.0.1')
        
        # Negative test (not a valid hostname either by RFC 952)
        os.environ['DISPLAY'] = '129.23.2:89'
        ip = dockerx.DockerLauncher.get_ip_from_display()
        self.assertFalse(ip)
    
    def test_get_port_from_display(self):
        # Positive IPv4:port test
        os.environ['DISPLAY'] = '123.4.5.6:89'
        port = dockerx.DockerLauncher.get_port_from_display()
        self.assertEqual(port, 6089)
        
        # Positive hostname:port test
        os.environ['DISPLAY'] = 'localhost:8'
        port = dockerx.DockerLauncher.get_port_from_display()
        self.assertEqual(port, 6008)

        # Positive :port test
        os.environ['DISPLAY'] = ':3'
        port = dockerx.DockerLauncher.get_port_from_display()
        self.assertEqual(port, 6003)

        # Negative test
        os.environ['DISPLAY'] = '127.0.0.1:no_port_for_you'
        port = dockerx.DockerLauncher.get_port_from_display()
        self.assertFalse(port)
    
    def test_function_to_detect_port_in_use(self, host='127.0.0.1', 
                                            port=50324, delay=1):
        # Check that our function does not detect any listening server
        self.assertFalse(is_port_in_use(host, port))

        # Launch netcat server
        process = subprocess.Popen(['nc', '-l', host, str(port)], 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(delay)

        # Check that our function can detect the listening server
        self.assertTrue(is_port_in_use(host, port))
        
        # Wait for netcat to finish
        exit_code = process.wait()

    def test_tcp_socket_detection(self, host='127.0.0.1', base_port=6000,
                                  offset=50, delay=1):
        # Find a port that is not in use
        port = base_port + offset
        while is_port_in_use(host, port): 
            offset += 1 
            port = base_port + offset

        # Set the DISPLAY pointing to the unused port
        os.environ['DISPLAY'] = ':' + str(offset)
        
        # Run an X11 dummy TCP server
        process = subprocess.Popen(['nc', '-l', host, str(port)], 
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(delay)

        # Check that we are able to detect dummy X11 TCP server
        socket_type = dockerx.DockerLauncher.get_x11_server_socket_type()
        self.assertEqual(socket_type, 'tcp')

    def test_unix_socket_detection(self):
        host = ''
        offset = 99
        os.environ['DISPLAY'] = host + ':' + str(offset)

        # Create dummy unix socket
        pathlib.Path('/tmp/.X11-unix/X' + str(offset)).touch()
        socket_type = dockerx.DockerLauncher.get_x11_server_socket_type()
        self.assertEqual(socket_type, 'unix')

    def test_negative_socket_deteection(self):
        os.environ['DISPLAY'] = ':96'
        socket_type = dockerx.DockerLauncher.get_x11_server_socket_type()
        self.assertFalse(socket_type)

if __name__ == '__main__':
    unittest.main()
