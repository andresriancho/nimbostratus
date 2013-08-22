import logging

from boto.iam import IAMConnection
from core.common_arguments import add_common_arguments


def cmd_arguments(subparsers):
    #
    # dump-role-permissions subcommand help
    #
    _help = 'Dump the permissions for the currently configured credentials'
    parser = subparsers.add_parser('dump-permissions', help=_help)
    
    add_common_arguments(parser)
    
    return subparsers

def cmd_handler(args):
    '''
    Main entry point for the sub-command.
    
    :param args: The command line arguments as parsed by argparse
    '''
    logging.debug('Starting dump-permissions')
    
    # First, check if we're the root account
    if check_root_account(args.access_key, args.secret_key, args.token):
        return
    
    # Try to access this information from the IAM service, which can fail
    # because the current credentials have no access to that API
    '''
    conn = IAMConnection()
    get_all_user_policies(user_name, marker=None, max_items=None)
    get_user_policy(user_name, policy_name)
    '''
    # Bruteforce the permissions

def check_root_account(access_key, secret_key, token):
    '''
    Do we have root account? The trick here is to enumerate all users and
    check if the access key provided is in the ones assigned to a user. This
    works because root accounts don't have a user associated to them.
    
    http://docs.aws.amazon.com/general/latest/gr/root-vs-iam.html
    '''
    if token:
        # Instance profiles don't have root account level
        return False
    
    try:
        conn = IAMConnection(aws_access_key_id=access_key,
                             aws_secret_access_key=secret_key)
    except Exception, e:
        # Root has access to IAM
        logging.debug('Failed to connect to IAM: "%s"' % e.error_message)
        logging.debug('Not an AWS root account')
        return False
    
    try:
        '''
        {u'users': [{u'path': u'/', u'create_date': u'2013-05-31T14:16:56Z',
                     u'user_id': u'AIDAI5L47MH36FQHRNI4A',
                     u'arn': u'arn:aws:iam::334918212912:user/ses-smtp-user.20130531-111624',
                     u'user_name': u'ses-smtp-user.20130531-111624'}], u'is_truncated': u'false'}}}
        '''
        users_list = conn.get_all_users()['list_users_response']['list_users_result']['users']
        for user_data in users_list:
            user_name = user_data['user_name']
            logging.debug('Getting access keys for user %s' % user_name)

            access_keys_response = conn.get_all_access_keys(user_name)
            access_keys = access_keys_response['list_access_keys_response']['list_access_keys_result']['access_key_metadata']
            
            for access_key in access_keys:
                if access_key['access_key_id'] == access_key:
                    msg = 'Since user %s has the configured access key, these'\
                          ' credentials do not belong to an AWS root account.'
                    logging.debug(msg % user_name)
                    return False
                
    except Exception, e:
        # Root has access to IAM
        logging.debug('Failed to enumerate users and access keys: "%s"' % e.error_message)
        logging.debug('Not an AWS root account')
        return False
    
    logging.info('The provided credentials are for an AWS root account!')
    
    return True