import argparse

from core.log_handler import configure_logging 

SUBCOMMANDS = {
               'snapshot-rds': 'core.snapshot_rds.command',
               'celery-pickle-exploit': 'core.celery_exploit.command',
               'create-iam-user': 'core.create_iam_user.command',
               'dump-ec2-metadata': 'core.dump_ec2_metadata.command',
               'dump-credentials': 'core.dump_credentials.command',
               'dump-permissions': 'core.dump_permissions.command',
               }


def parse_args():
    parser = argparse.ArgumentParser(prog='nimbostratus')
    parser.add_argument("-v", "--verbosity", help="Increase output verbosity",
                        action="store_true")
    
    subparsers = parser.add_subparsers(help='Available subcommands',
                                       dest="subparser_name")
    
    for subcommand, module_name in SUBCOMMANDS.iteritems():
        _temp = __import__(module_name, globals(), locals(), ['cmd_arguments'], -1)
        _temp.cmd_arguments(subparsers)
    
    args = parser.parse_args()
    
    return args

def cmd_handler():
    '''
    This is the "main" which is called by "nimbostratus" file.
    '''
    args = parse_args()

    configure_logging(args.verbosity)

    module_name = SUBCOMMANDS[args.subparser_name]
    _temp = __import__(module_name, globals(), locals(), ['cmd_handler'], -1)
    _temp.cmd_handler(args)
