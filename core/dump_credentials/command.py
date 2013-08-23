import logging

from boto.provider import get_default
from boto.utils import get_instance_metadata

from core.utils.mangle import metadata_hook
from core.common_arguments import add_mangle_arguments


def cmd_arguments(subparsers):
    #
    # dump-credentials subcommand help
    #
    _help = 'Dump the credentials configured in the current host.'
    parser = subparsers.add_parser('dump-credentials', help=_help)
    
    add_mangle_arguments(parser)
    
    return subparsers

@metadata_hook
def cmd_handler(args):
    '''
    Main entry point for the sub-command.
    
    :param args: The command line arguments as parsed by argparse
    '''
    logging.debug('Starting dump-credentials')
    
    get_credentials()
    
def get_credentials():
    get_metadata_credentials()
    get_local_credentials()
    
def get_metadata_credentials():
    meta_data = get_instance_metadata(data='meta-data/iam/security-credentials',
                                      num_retries=1, timeout=2)
    if not meta_data:
        logging.debug('Failed to contact instance meta-data server.')
    else:
        security = meta_data.values()[0]
        access_key = security['AccessKeyId']
        secret_key = security['SecretAccessKey']
        security_token = security['Token']
    
        print_credentials(access_key, secret_key, security_token)

def get_local_credentials():
    provider = get_default()
    provider.get_credentials()
    
    access_key = provider.get_access_key()
    secret_key = provider.get_secret_key()
    security_token = provider.get_security_token()
    
    print_credentials(access_key, secret_key, security_token)

def print_credentials(access_key, secret_key, security_token):
    logging.info('Found credentials')
    logging.info('  Access key: %s' % access_key)
    logging.info('  Secret key: %s' % secret_key)
    if security_token:
        logging.info('  Token: %s' % security_token)
    logging.info('')
