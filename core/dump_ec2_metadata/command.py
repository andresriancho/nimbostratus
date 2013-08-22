def cmd_arguments(subparsers):
    #
    # dump-ec2-metadata subcommand help
    #
    _help = 'Dump EC2 instance meta-data from http://169.254.169.254/'
    parser = subparsers.add_parser('dump-ec2-metadata', help=_help)
    
    _help = 'The URL which acts as a proxy and allows us to perform queries'\
            ' to the instance meta-data. Example http://host.tld/?url=%s'\
            ' Please note that for a successful exploitation you need'\
            ' to edit the "extract_data_from_proxy" function.'
    parser.add_argument('--proxy-url', help=_help)

    
    return subparsers

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
