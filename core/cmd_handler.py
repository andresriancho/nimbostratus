import argparse

from core.snapshot_rds.command import cmd_arguments as snap_cmd_args
from core.celery_exploit.command import cmd_arguments as celery_cmd_args


def parse_args():
    parser = argparse.ArgumentParser(prog='nimbostratus')
    parser.add_argument("-v", "--verbosity", help="Increase output verbosity",
                        action="store_true")
    
    subparsers = parser.add_subparsers(help='Available subcommands')
    
    snap_cmd_args(subparsers)
    celery_cmd_args(subparsers)
    
    args = parser.parse_args()
    
    return args

def cmd_handler():
    '''
    This is the "main" which is called by "nimbostratus" file.
    '''
    args = parse_args()