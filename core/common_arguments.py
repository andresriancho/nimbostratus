def add_common_arguments(parser):
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

