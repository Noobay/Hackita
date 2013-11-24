from bottle import run, route, template, get, post, default_app
from bywaf import WAFterpreter
import os,sys
from cStringIO import StringIO

from multiprocessing import Process

@get('/index') # or @route('/')
def web_input():
    return '''
        <form action="/" method="post">
            Input: <input name="input" type="text" />
            <input value="input" type="submit" />
        </form>
    '''


@post('/index')
def proc_input():
    w_input = request.forms.get('input')

    args = w_input.split(' ', 1)

    outText = " "
    try:
        newfunc = getattr(wafterpreter, 'do_'+args[0])
        print args[0]
        if len(args) < 2:
            args.append("")
        else:
            pass
        newfunc(args[1])
    except AttributeError:
        return 'no such function exists'
    except IndexError:
        return 'try another function'


    return template('<pre> {} </pre> <script> alert("OS"); </script>'.format(waf_out.getvalue()))
    output.close()

if __name__ == "__main__":

    inp    = sys.stdin
    waf_out = StringIO()
    wafterpreter = WAFterpreter(stdin=inp, stdout=waf_out)

application = default_app()


