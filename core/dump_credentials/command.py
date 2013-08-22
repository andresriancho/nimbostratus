import logging

from boto.core.credentials import AllCredentialFunctions


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
    get_credentials()
    
def get_credentials(persona='default'):
    for cred_fn in AllCredentialFunctions:
        credentials = cred_fn(persona=persona,
                              access_key_name='access_key',
                              secret_key_name='secret_key')
        if credentials:
            logging.info('Found credentials using "%s"' % cred_fn.__name__)
            logging.info('  Access key: %s' % credentials.access_key)
            logging.info('  Secret key: %s' % credentials.secret_key)
            if credentials.token:
                logging.info('  Token: %s' % credentials.token)
            logging.info('')
    return credentials