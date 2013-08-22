def add_credential_arguments(parser):
    '''
    Adds the following command line arguments to the parser:
         * `--access-key`
         * `--secret-key`
         * `--token` , which is only used when the credentials were extracted from the instance profile.
    '''
    _help = 'AWS access key'
    parser.add_argument('--access-key', help=_help, required=True)

    _help = 'AWS secret key'
    parser.add_argument('--secret-key', help=_help, required=True)

    _help = 'AWS instance profile token'
    parser.add_argument('--token', help=_help, required=False, default=None)

def add_region_arguments(parser):
    _help = 'AWS region to connect to'
    parser.add_argument('--region', help=_help, required=True, default=None)

def add_mangle_arguments(parser):
    _help = 'Retrieving EC2 meta-data information from the instance http://169.254.169.254/'\
            ' is possible if there is a vulnerability in the remote system which'\
            ' allows us to proxy the HTTP GET requests through it. This parameter'\
            ' specifies a function which will receive all the intercepted HTTP GET'\
            ' requests made by boto to 169.254.169.254 and let you implement the'\
            ' way you want to handle them. An example implementation lives in'\
            ' core.utils.mangle.mangle . Example: --mangle-function=core.utils.mangle.mangle'
    parser.add_argument('--mangle-function', help=_help, required=False, default=None)
