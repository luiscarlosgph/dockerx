"""
@brief  Unit tests for the launcher of docker containers with X11 support.
@author Luis C. Garcia Peraza Herrera (luiscarlos.gph@gmail.com).
@date   15 April 2021 -> Happy birthday to my sister!
"""

import unittest
import os
import socket
import pathlib
import threading

# My imports
import dockerl

def dummy_tcp_server(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    address = (host, port)
    sock.bind(address) 
    sock.listen(1)
    (client_sock, _) = sock.accept()
    client_sock.close()
    sock.close()

class TestDockerLauncher(unittest.TestCase):

    def test_get_ip_from_interface(self):
        ip = dockerl.DockerLauncher.get_ip_from_interface('lo')
        self.assertEqual(ip, '127.0.0.1')
    
    def test_get_ip_from_display(self):
        # Positive IP test
        os.environ['DISPLAY'] = '192.168.69.96:99'
        ip = dockerl.DockerLauncher.get_ip_from_display()
        self.assertEqual(ip, '192.168.69.96')

        # Positive hostname test
        os.environ['DISPLAY'] = 'localhost:23'
        ip = dockerl.DockerLauncher.get_ip_from_display()
        self.assertEqual(ip, '127.0.0.1')
        
        # Negative test (not a valid hostname either by RFC 952)
        os.environ['DISPLAY'] = '129.23.2:89'
        ip = dockerl.DockerLauncher.get_ip_from_display()
        self.assertFalse(ip)
    
    def test_get_port_from_display(self):
        # Positive IPv4:port test
        os.environ['DISPLAY'] = '123.4.5.6:89'
        port = dockerl.DockerLauncher.get_port_from_display()
        self.assertEqual(port, 6089)
        
        # Positive hostname:port test
        os.environ['DISPLAY'] = 'localhost:8'
        port = dockerl.DockerLauncher.get_port_from_display()
        self.assertEqual(port, 6008)

        # Positive :port test
        os.environ['DISPLAY'] = ':3'
        port = dockerl.DockerLauncher.get_port_from_display()
        self.assertEqual(port, 6003)

        # Negative test
        os.environ['DISPLAY'] = '127.0.0.1:no_port_for_you'
        port = dockerl.DockerLauncher.get_port_from_display()
        self.assertFalse(port)

    def test_tcp_socket_detection(self):
        # Setup DISPLAY
        offset = 28
        os.environ['DISPLAY'] = ':' + str(offset)

        # Run an X11 dummy TCP server
        host = 'localhost'
        port = 6000 + offset
        thread = threading.Thread(target=dummy_tcp_server, args=(host, port))
        thread.start()

        # Check that we are able to detect dummy X11 TCP server
        socket_type = dockerl.DockerLauncher.get_x11_server_socket_type()
        self.assertEqual(socket_type, 'tcp')

        thread.join()

    def test_unix_socket_detection(self):
        host = ''
        offset = 99
        os.environ['DISPLAY'] = host + ':' + str(offset)

        # Create dummy unix socket
        pathlib.Path('/tmp/.X11-unix/X' + str(offset)).touch()
        socket_type = dockerl.DockerLauncher.get_x11_server_socket_type()
        self.assertEqual(socket_type, 'unix')

    def test_negative_socket_deteection(self):
        os.environ['DISPLAY'] = ':96'
        socket_type = dockerl.DockerLauncher.get_x11_server_socket_type()
        self.assertFalse(socket_type)

if __name__ == '__main__':
    unittest.main()
