import time
import random
import string
import logging

from boto.rds import connect_to_region

from core.common_arguments import add_region_arguments, add_credential_arguments

SUCCESS_MESSAGE = '''\
Anyone can connect to this MySQL instance at:
    - Host: %s
    - Port: %s
    
    Using root:
        mysql -u %s -p%s -h %s
'''


def cmd_arguments(subparsers):
    #
    # snapshot-rds subcommand help
    #
    snap_help = 'Creates a snapshot of an RDS instance and restores it with a'\
                ' different "root" password in order to access all it\'s'\
                ' information.'
    parser_snapshot = subparsers.add_parser('snapshot-rds', help=snap_help)
    
    _help = 'The "root" password to use for the RDS clone.'\
            'Must be 4-15 alphanumeric characters.'
    parser_snapshot.add_argument('--password', help=_help, required=True)

    _help = 'The RDS instance name to clone.'
    parser_snapshot.add_argument('--rds-name', help=_help, required=True)

    add_credential_arguments(parser_snapshot)
    add_region_arguments(parser_snapshot)

    return subparsers

def cmd_handler(args):
    '''
    Main entry point for the sub-command.
    
    :param args: The command line arguments as parsed by argparse
    '''
    logging.debug('Starting snapshot-rds')
    
    try:
        conn = connect_to_region(args.region,
                                 aws_access_key_id=args.access_key,
                                 aws_secret_access_key=args.secret_key,
                                 security_token=args.token)
    except Exception, e:
        logging.critical('Failed to connect to RDS: "%s"' % e.error_message)
        return
    
    try:
        instances = conn.get_all_dbinstances(args.rds_name)
        db = instances[0]
    except Exception, e:
        logging.critical('No RDS instance with name "%s"' % (args.rds_name,
                                                             e.error_message))
        return
    
    snapshot_name = ''.join([random.choice(string.ascii_lowercase) for _ in xrange(9)])
    security_group_name = ''.join([random.choice(string.ascii_lowercase) for _ in xrange(9)])
    restored_instance = 'restored-%s' % snapshot_name
    
    try:
        db.snapshot(snapshot_name)
        
        logging.info('Waiting for snapshot to complete in AWS... (this takes at least 5m)')
        wait_for_available_db(conn, args.rds_name)
        
    except Exception, e:
        logging.critical('Failed to snapshot: "%s"' % e.error_message)
        return
    
    try:
        db_clone = conn.restore_dbinstance_from_dbsnapshot(snapshot_name,
                                                           restored_instance,
                                                           'db.m1.small')
        
        logging.info('Waiting for restore process in AWS... (this takes at least 5m)')
        wait_for_available_db(conn, restored_instance)
        
    except Exception, e:
        logging.critical('Failed to restore DB instance: "%s"' % e.error_message)
        return
    
    try:
        conn.modify_dbinstance(id=restored_instance,
                               master_password=args.password,
                               apply_immediately=True)
    except Exception, e:
        msg = 'Failed to change the newly created RDS master password: "%s"'
        logging.critical(msg % e.error_message)
    
    
    logging.debug('Creating a DB security group which allows connections from'
                  ' any location and applying it to the newly created RDS'
                  ' instance.')
    
    try:
        # Very insecure, everyone can connect to this MySQL instance
        sg = conn.create_dbsecurity_group(security_group_name, 'All hosts can connect')
        sg.authorize(cidr_ip='0.0.0.0/0')
        
        # Just in case we wait for it to be available
        db_clone = wait_for_available_db(conn, restored_instance)
        
        db_clone.modify(security_groups=[sg])
    except Exception, e:
        logging.critical('Failed to create and apply DB security group: "%s"' % e.error_message)
        return
    else:
        host, port = db_clone.endpoint
        logging.info(SUCCESS_MESSAGE % (host, port,
                                        'root', args.password, host))

def wait_for_available_db(conn, db_name):
    time.sleep(30)
    while True:
        db = conn.get_all_dbinstances(db_name)[0]
        if db.status == 'available' and db.endpoint is not None:
            break
        else:
            logging.debug('Waiting...')
            time.sleep(30)
    
    return db