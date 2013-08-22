def cmd_arguments(subparsers):
    #
    # create-iam-user subcommand help
    #
    _help = 'Use the current credentials to create a user with all AWS'\
            ' privileges. When the current user has iam:* but other'\
            ' permissions are restricted, this acts like a privilege'\
            ' escalation.'
    parser = subparsers.add_parser('create-iam-user', help=_help)
    
    return subparsers