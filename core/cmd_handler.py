import argparse

from core.snapshot_rds.command import cmd_arguments as snap_cmd_args
from core.celery_exploit.command import cmd_arguments as celery_cmd_args
from core.create_iam_user.command import cmd_arguments as create_user_args
from core.dump_ec2_metadata.command import cmd_arguments as dump_meta_args
from core.dump_credentials.command import cmd_arguments as dump_creds_args
from core.dump_permissions.command import cmd_arguments as dump_perms_args


def parse_args():
    parser = argparse.ArgumentParser(prog='nimbostratus')
    parser.add_argument("-v", "--verbosity", help="Increase output verbosity",
                        action="store_true")
    
    subparsers = parser.add_subparsers(help='Available subcommands')
    
    for custom_subparsers in (snap_cmd_args, celery_cmd_args, create_user_args,
                              dump_meta_args, dump_creds_args, dump_perms_args):
        custom_subparsers(subparsers)
    
    args = parser.parse_args()
    
    return args

def cmd_handler():
    '''
    This is the "main" which is called by "nimbostratus" file.
    '''
    args = parse_args()