# coding=utf-8
########################
#bywaf core methods, to be loaded on init
########################

import urllib2
intro = '''CORE.py loaded'''


options = {'Option': ['Value', 'Defualt', 'Required', 'Description']}


#example method
def do_ssl(args):
    '''checks if a server uses SSL'''

    #additinal arguments
    options = ''
    verbose = False

    if len(args.split()) > 1:
        addr, options = args.split(' ', 1)
    else:
        addr = args
    if(options == 'v' or options == '-v'):
        verbose = True

    # auto complete http to https
    if(addr.split(':')[0]=='http'):
        addr = 'https'+addr[4:]
        app.print_line(addr)

    # auto complete https if no prefix is given
    elif('https://' not in addr):
        addr = 'https://'+addr


    try:
        urllib2.urlopen(addr)
        if(verbose):
            app.print_line('this server supports SSL')
        return True
    except urllib2.URLError as e:
        # fail only if connection did not respond or refused connection
        # e.args[0][0] is the error code
        try:
            if e.args[0][0] == 10060 or e.args[0][0] == 10061:
                if(verbose):
                    app.print_line('this server does not support SSL')
            else:
                app.print_line('enter a valid url')
            return False
        except IndexError:
            return False