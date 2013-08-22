import json
import pprint
import urllib
import re
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
    success, permissions = check_via_iam(args.access_key, args.secret_key, args.token)
    if success:
        print_permissions(permissions)
        return
    
    # Bruteforce the permissions
    pass

def print_permissions(permissions):
    for permission_obj in permissions:
        logging.info(pprint.pformat(permission_obj))

def check_via_iam(access_key, secret_key, token):
    '''
    Connect to IAM and try to retrieve my policy.
    '''
    try:
        conn = IAMConnection(aws_access_key_id=access_key,
                             aws_secret_access_key=secret_key)
    except Exception, e:
        logging.debug('Failed to connect to IAM: "%s"' % e.error_message)
        logging.debug('Account has no access to IAM')
        return False, None

    user = get_current_user(conn, access_key)
    
    if user is None:
        return False, None

    try:
        all_user_policies = conn.get_all_user_policies(user)
    except Exception, e:
        msg = 'Account has no privileges to get all user policies: "%s"'
        logging.debug(msg % e.error_message)
        return False, None

    policy_names = all_user_policies['list_user_policies_response']['list_user_policies_result']['policy_names']
    
    permissions = []
    
    for policy_name in policy_names:
        try:
            user_policy = conn.get_user_policy(user, policy_name)
        except:
            msg = 'Account has no privileges to get user policy: "%s"'
            logging.debug(msg % e.error_message)
            return False, None
        else:
            policy_document = user_policy['get_user_policy_response']['get_user_policy_result']['policy_document']
            policy_document = urllib.unquote(policy_document)
            policy_document = json.loads(policy_document)
            permissions.append(policy_document)
    
    return True, permissions

def get_current_user(conn, access_key):
    '''
    Try different tricks to get the current user name.
    
    :return: A string containing the username
    '''
    for technique in (get_current_user_from_error, get_user_from_key):
        user = technique(conn, access_key)
        if user is not None:
            return user
    
    return None

def get_user_from_key(conn, access_key):
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
        
        for access_key_data in access_keys:
            if access_key_data['access_key_id'] == access_key:
                logging.debug('User for key %s is %s' % (access_key,
                                                         access_key_data['user_name']))
                return access_key_data['user_name']
                

def get_current_user_from_error(conn, access_key):
    try:
        conn.get_account_summary()
    except Exception, e:
        # User: arn:aws:iam::334918212912:user/pedro is not authorized to perform: ...
        message = e.error_message
    else:
        return None
    
    try:
        user = re.search('iam::.*?:user/(.*?) ', message).group(1)
    except:
        return None
    else:
        logging.debug('Current user is %s' % user)
        return user

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
        conn.get_account_summary()
    except Exception, e:
        # Root has access to IAM account summary
        logging.debug('Failed to retrieve IAM account summary: "%s"' % e.error_message)
        logging.debug('Not an AWS root account')
        return False
    
    try:
        user = get_user_from_key(conn, access_key)
    except Exception, e:
        # Root has access to IAM
        logging.debug('Failed to enumerate users and access keys: "%s"' % e.error_message)
        logging.debug('Not an AWS root account')
        return False
    else:
        if user is not None:
            logging.debug('These credentials belong to %s, not to the root account' % user)
            return False
            
    logging.info('The provided credentials are for an AWS root account! These'\
                 ' credentials have ALL permissions.')
    
    return True