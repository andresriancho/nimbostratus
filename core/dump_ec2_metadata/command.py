import logging
import pprint

from boto.utils import (get_instance_userdata,
                        get_instance_identity,
                        get_instance_metadata)

from core.common_arguments import add_mangle_arguments
from core.utils.mangle import metadata_hook


def cmd_arguments(subparsers):
    #
    # dump-ec2-metadata subcommand help
    #
    _help = 'Dump EC2 instance meta-data from http://169.254.169.254/'
    parser = subparsers.add_parser('dump-ec2-metadata', help=_help)

    add_mangle_arguments(parser)
        
    return subparsers

@metadata_hook
def cmd_handler(args):
    '''
    Main entry point for the sub-command.
    
    :param args: The command line arguments as parsed by argparse
    '''
    logging.debug('Starting dump-ec2-metadata')
    
    handle_instance_metadata()
    handle_instance_identity()
    handle_instance_userdata()

def handle_instance_metadata():
    '''
    {'instance-type': 't1.micro', 
     'instance-id': 'i-807e52d7', 
     'iam': {'info': {'InstanceProfileArn': 'arn:aws:iam::334918212912:instance-profile/django_frontend_nimbostratus',
                      'InstanceProfileId': 'AIPAIMOLOJUADL3JWAN56',
                      'Code': 'Success',
                      'LastUpdated':
                      '2013-08-22T20:07:44Z'},
            'security-credentials': {'django_frontend_nimbostratus':
                                        {'Code': 'Success',
                                         'LastUpdated': '2013-08-22T20:08:22Z',
                                         'AccessKeyId': 'ASIAJ432XXHBO2V3R5OA',
                                         'SecretAccessKey': 'x+M61ZRT/TgUZ3UnGtjY40wOK9UTeTilnNol98kX',
                                         'Token': 'glN...AU',
                                         'Expiration': '2013-08-23T02:15:14Z',
                                         'Type': 'AWS-HMAC'}}},
     'local-hostname': 'ip-10-130-77-91.ap-southeast-1.compute.internal',
     'network': {'interfaces': {'macs': {'12:31:41:00:4e:91': {'local-hostname': 'ip-10-130-77-91.ap-southeast-1.compute.internal',
                                                               'public-hostname': 'ec2-54-254-24-239.ap-southeast-1.compute.amazonaws.com',
                                                               'public-ipv4s': '54.254.24.239',
                                                               'mac': '12:31:41:00:4e:91',
                                                               'owner-id': '334918212912',
                                                               'local-ipv4s': '10.130.77.91',
                                                               'device-number': '0'}}}},
     'hostname': 'ip-10-130-77-91.ap-southeast-1.compute.internal',
     'ami-id': 'ami-a02f66f2',
     'kernel-id': 'aki-fe1354ac',
     'instance-action': 'none',
     'profile': 'default-paravirtual',
     'reservation-id': 'r-e9efbebe',
     'security-groups': 'django_frontend_nimbostratus_sg',
     'metrics': {'vhostmd': '<?xml version="1.0" encoding="UTF-8"?>'},
     'mac': '12:31:41:00:4E:91',
     'public-ipv4': '54.254.24.239',
     'ami-manifest-path': '(unknown)',
     'local-ipv4': '10.130.77.91',
     'placement': {'availability-zone': 'ap-southeast-1a'},
     'ami-launch-index': '0',
     'public-hostname': 'ec2-54-254-24-239.ap-southeast-1.compute.amazonaws.com',
     'public-keys': {'django_frontend_nimbostratus': ['ssh-rsa A...jxT django_frontend_nimbostratus', '']},
     'block-device-mapping': {'ami': '/dev/sda1', 'root': '/dev/sda1', 'ephemeral0': 'sdb'}
    }
    '''
    meta_data = get_instance_metadata()
    logging.debug(pprint.pformat(meta_data))
    
    logging.info('Instance type: %s' % meta_data['instance-type'])
    logging.info('AMI ID: %s' % meta_data['ami-id'])
    logging.info('Security groups: %s' % meta_data['security-groups'])
    logging.info('Availability zone: %s' % meta_data['placement']['availability-zone'])
    
def handle_instance_identity():
    '''
    {'document': {'devpayProductCodes': None,
                  'availabilityZone': 'ap-southeast-1a',
                  'instanceId': 'i-807e52d7',
                  'region': 'ap-southeast-1',
                  'imageId': 'ami-a02f66f2',
                  'version': '2010-08-31',
                  'architecture': 'x86_64',
                  'billingProducts': None,
                  'kernelId': 'aki-fe1354ac',
                  'ramdiskId': None,
                  'privateIp': '10.130.77.91',
                  'instanceType': 't1.micro',
                  'pendingTime': '2013-08-22T19:24:30Z',
                  'accountId': '334918212912'},
     'pkcs7': '...'}
    '''
    identity = get_instance_identity()
    logging.debug(pprint.pformat(identity))
    
    logging.info('Architecture: %s' % identity['document']['architecture'])
    logging.info('Private IP: %s' % identity['document']['privateIp'])

def handle_instance_userdata():
    '''
    Since this is too long, store it in a file.
    '''
    user_data = get_instance_userdata()
    if user_data:
        file('user-data.txt', 'w').write(user_data)
        logging.info('User data script was written to user-data.txt')

def extract_data_from_proxy(http_response):
    '''
    :param http_response: A requests module HTTP response object which is the
                          result of sending a query for the meta-data via the
                          proxy URL.
    :return: Usually the http response body contains a header, the information
             we need and a footer. This function should remove the header and
             footer and return the important information.
    '''
    return http_response.text
