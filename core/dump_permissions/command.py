def cmd_arguments(subparsers):
    #
    # dump-role-permissions subcommand help
    #
    _help = 'Dump the permissions for the currently configured credentials'
    parser = subparsers.add_parser('dump-permissions', help=_help)
    
    return subparsers