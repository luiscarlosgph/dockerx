"""
@brief  Launch a docker container with X11 support.
@author Luis Carlos Garcia Peraza Herrera (luiscarlos.gph@gmail.com).
@date   2 March 2021.
"""
import argparse
import sys
import dockerx


def msg(param: str):
    """
    @param[in]  param  Command line option, e.g.: '--image'.
    @returns the help message for each command line parameter.
    """
    msg = {
        '--image'  : 'Docker image name.',
        '--nvidia' : 'Activate the use of nvidia runtime. Default is 0.',  
        '--command': 'Command to be executed in the container.',
        '--volume' : 'Syntax: <source>:<target_path_in_container>. ' \
                     + 'The <source> can be either a Docker volume ' \
                     + 'or a local path in the host.',
        '--env'    : 'Syntax: \'<key>=<value>\'.',
    }
    return msg[param]


def parse_command_line_parameters(parser):
    parser.add_argument('--image', required=True, type=str, 
                        help=msg('--image'))
    parser.add_argument('--nvidia', required=False, default=False, type=int,
                        help=msg('--nvidia'))
    parser.add_argument('--command', required=False, default=None, type=str,
                        help=msg('--command'))
    parser.add_argument('--volume', required=False, nargs='*', type=str, 
                        default=[], help=msg('--volume'))
    parser.add_argument('--env', required=False, nargs='*', type=str,
                        default=[], help=msg('--env'))

    args = parser.parse_args()
    args.nvidia = bool(int(args.nvidia))
    args.command = None if args.command == 'None' else args.command
    return args


def parse_env(list_of_args: list[str]):
    """
    @brief Convert the list of --env strings passed in the command line into
           a dictionary for dockerx.DockerLauncer.launch_container().
    @param[in]  list_of_args  List of strings like 'DEEP=LEARNING'.
    @returns the dictionary of environment variables.
    """
    return {s.split('=')[0]: s.split('=')[1] for s in list_of_args}


def main():
    # Parse command line parameters
    parser = argparse.ArgumentParser()
    args = parse_command_line_parameters(parser)
    
    # Launch docker container
    dl = dockerx.DockerLauncher()
    container = dl.launch_container(args.image, command=args.command, 
            nvidia_runtime=args.nvidia, env_vars=parse_env(args.env))
        
    # Print info for the user
    sys.stdout.write("\nTo get a container terminal run:  ") 
    sys.stdout.write('docker exec -it ' + container.id[:12]  + " /bin/bash\n") 
    sys.stdout.write("To kill the container run:  ")
    sys.stdout.write('      docker kill ' + container.id[:12] + "\n")
    sys.stdout.write("To remove the container run:  ")
    sys.stdout.write('    docker rm ' + container.id[:12] + "\n\n")


if __name__ == '__main__':
    main()
