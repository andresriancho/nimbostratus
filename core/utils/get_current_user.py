import logging
import re


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
    try:
        users_list = conn.get_all_users()['list_users_response']['list_users_result']['users']
    except Exception, e:
        logging.debug('Failed to get all users: "%s"' % e.error_message)
        return None
    
    for user_data in users_list:
        user_name = user_data['user_name']
        logging.debug('Getting access keys for user %s' % user_name)

        try:
            access_keys_response = conn.get_all_access_keys(user_name)
        except Exception, e:
            logging.debug('Failed to get all access keys: "%s"' % e.error_message)
            return None

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