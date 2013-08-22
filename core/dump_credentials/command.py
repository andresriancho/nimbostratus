import logging


def cmd_arguments(subparsers):
    #
    # dump-credentials subcommand help
    #
    _help = 'Dump the credentials configured in the current host.'
    parser = subparsers.add_parser('dump-credentials', help=_help)
    
    return subparsers

def cmd_handler(args):
    '''
    Main entry point for the sub-command.
    
    :param args: The command line arguments as parsed by argparse
    '''
    logging.debug('Starting dump-credentials')