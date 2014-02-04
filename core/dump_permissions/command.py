import json
import pprint
import urllib
import logging

from boto.iam import IAMConnection
from boto.ec2 import EC2Connection
from boto.sqs.connection import SQSConnection
from boto.rds import RDSConnection

from core.common_arguments import add_credential_arguments
from core.utils.get_current_user import get_current_user, get_user_from_key


def cmd_arguments(subparsers):
    #
    # dump-role-permissions subcommand help
    #
    _help = 'Dump the permissions for the currently configured credentials'
    parser = subparsers.add_parser('dump-permissions', help=_help)
    
    add_credential_arguments(parser)
    
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
    permissions = bruteforce_permissions(args.access_key, args.secret_key, args.token)
    print_permissions(permissions)

def print_permissions(permissions):
    if not permissions:
        logging.warn('No permissions could be dumped.')
        return
    
    for permission_obj in permissions:
        logging.info(pprint.pformat(permission_obj))

def bruteforce_permissions(access_key, secret_key, token):
    '''
    Will check the most common API calls and verify if we have access to them.
    '''
    logging.debug('Bruteforcing permissions')
    # Some common actions are:
    #    u'autoscaling:Describe*',
    #    u'ec2:Describe*',
    #    u's3:Get*',
    #    u's3:List*',
    action_list = []
    permissions = []
    
    BRUTEFORCERS = (bruteforce_ec2_permissions, bruteforce_sqs_permissions,
                    bruteforce_rds_permissions)
    
    for bruteforcer in BRUTEFORCERS:
        action_list.extend(bruteforcer(access_key, secret_key, token))
    
    bruteforced_perms = {u'Statement': [{u'Action': action_list,
                                         u'Effect': u'Allow',
                                         u'Resource': u'*'}],
                         u'Version': u'2012-10-17'}
    
    if action_list:
        permissions.append(bruteforced_perms)
    else:
        logging.warn('No actions could be bruteforced.')

    return permissions

def bruteforce_ec2_permissions(access_key, secret_key, token):
    tests = [('DescribeImages', 'get_all_images', (), {'owners': ['self',]}),
             ('DescribeInstances', 'get_all_instances', (), {}),
             ('DescribeInstanceStatus', 'get_all_instance_status', (), {}),]
    return generic_permission_bruteforcer(EC2Connection, access_key, secret_key,
                                          token, tests)

def bruteforce_sqs_permissions(access_key, secret_key, token):
    tests = [('ListQueues', 'get_all_queues', (), {}),]
    return generic_permission_bruteforcer(SQSConnection, access_key, secret_key,
                                          token, tests)

def bruteforce_rds_permissions(access_key, secret_key, token):
    tests = [('DescribeDBInstances', 'get_all_dbinstances', (), {}),
             ('DescribeDBSecurityGroups', 'get_all_dbsecurity_groups', (), {}),
             ('DescribeDBSnapshots', 'get_all_dbsnapshots', (), {}),]
    
    return generic_permission_bruteforcer(RDSConnection, access_key, secret_key,
                                          token, tests)
    
def generic_permission_bruteforcer(connection_klass, access_key, secret_key, token,
                                   tests):
    actions = []
    
    try:
        conn = connection_klass(aws_access_key_id=access_key,
                                aws_secret_access_key=secret_key,
                                security_token=token)
    except Exception, e:
        logging.debug('Failed to connect: "%s"' % e.error_message)
        return actions
    
    actions = generic_method_bruteforcer(tests, conn)
    
    return actions
    

def generic_method_bruteforcer(tests, conn):
    actions = []
    
    for api_action, method_name, args, kwargs in tests:
        try:
            method = getattr(conn, method_name)
            method(*args, **kwargs)
        except Exception, e:
            logging.debug('%s is not allowed: "%s"' % (api_action, e.error_message))
        else:
            logging.debug('%s IS allowed' % api_action)
            actions.append(api_action)
    
    return actions

def check_via_iam(access_key, secret_key, token):
    '''
    Connect to IAM and try to retrieve my policy.
    '''
    try:
        conn = IAMConnection(aws_access_key_id=access_key,
                             aws_secret_access_key=secret_key,
                             security_token=token)
    except Exception, e:
        logging.debug('Failed to connect to IAM: "%s"' % e.error_message)
        logging.debug('Account has no access to IAM')
        return False, None

    user = get_current_user(conn, access_key)
    
    if user is None:
        return False, None

    logging.info('Current user %s' % user)

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
            break
        else:
            policy_document = user_policy['get_user_policy_response']['get_user_policy_result']['policy_document']
            policy_document = urllib.unquote(policy_document)
            policy_document = json.loads(policy_document)
            permissions.append(policy_document)

    all_groups = []
    all_group_policies = []
    
    try:
        all_groups_resp = conn.get_groups_for_user(user)
    except Exception, e:
        msg = 'Account has no privileges to get groups for user: "%s"'
        logging.debug(msg % e.error_message)

    for group in all_groups_resp['list_groups_for_user_response']['list_groups_for_user_result']['groups']:
        all_groups.append(group['group_name'])

    try:
        for group in all_groups:
            group_policies_resp = conn.get_all_group_policies(group)
            policy_names = group_policies_resp['list_group_policies_response']['list_group_policies_result']['policy_names']
            all_group_policies.extend(policy_names)
    except Exception, e:
        msg = 'Account has no privileges to get all group policies: "%s"'
        logging.debug(msg % e.error_message)

    for group in all_groups:
        for policy in all_group_policies:
            try:
                group_policy = conn.get_group_policy(group, policy)
            except:
                msg = 'Account has no privileges to get group policy: "%s"'
                logging.debug(msg % e.error_message)
                break
            else:
                policy_document = group_policy['get_group_policy_response']['get_group_policy_result']['policy_document']
                policy_document = urllib.unquote(policy_document)
                policy_document = json.loads(policy_document)
                permissions.append(policy_document)
            
    return bool(permissions), permissions


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
                             aws_secret_access_key=secret_key,
                             security_token=token)
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
