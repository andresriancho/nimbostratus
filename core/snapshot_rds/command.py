def cmd_arguments(subparsers):
    #
    # snapshot-rds subcommand help
    #
    snap_help = 'Creates a snapshot of an RDS instance and restores it with a'\
                ' different "root" password in order to access all it\'s'\
                ' information.'
    parser_snapshot = subparsers.add_parser('snapshot-rds', help=snap_help)
    
    pwd_help = 'The "root" password to use for the RDS clone'
    parser_snapshot.add_argument('--password', help=pwd_help)

    return subparsers