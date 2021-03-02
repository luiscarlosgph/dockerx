##
# @brief  Launch a docker container with X11 support.
# @author Luis Carlos Garcia Peraza Herrera (luiscarlos.gph@gmail.com).
# @date   2 March 2021.

import argparse
import sys
import dockerl

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
    
    # Launch docker container
    dl = dockerl.DockerLauncher()
    container = dl.launch_container(args.image, command='sleep infinity', 
        nvidia_runtime=args.nvidia)
        
    # Print info for the user
    sys.stdout.write("\nTo get a container terminal run:  ") 
    sys.stdout.write('docker exec -it ' + container.id[:12]  + " /bin/bash\n") 
    sys.stdout.write("To kill the container run:  ") 
    sys.stdout.write('      docker kill ' + container.id[:12] + "\n\n") 

if __name__ == '__main__':
    main()
