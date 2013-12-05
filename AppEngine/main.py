#!/usr/bin/env python
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from bottle import request, get, post, default_app
from bywaf import WAFterpreter
from urllib2 import urlopen
import sys
from cStringIO import StringIO

style = '''

    <style>
    textarea{
    width:100%;
    display:block;
    max-width:100%;
    line-height:1.5;
    padding:15px 15px 30px;
    border-radius:3px;
    border:1px solid #F7E98D;
    transition:box-shadow 0.5s ease;
    box-shadow:0 4px 6px rgba(0,0,0,0.1);
    font-smoothing:subpixel-antialiased;
    background:linear-gradient(#F9EFAF, #F7E98D);
    background:-o-linear-gradient(#F9EFAF, #F7E98D);
    background:-ms-linear-gradient(#F9EFAF, #F7E98D);
    background:-moz-linear-gradient(#F9EFAF, #F7E98D);
    background:-webkit-linear-gradient(#F9EFAF, #F7E98D);
    height:100%;
    }
    input{
    border:1px solid #000000;
    border-radius:8px;
    box-shadow:5px 4px 6px rgba(0,0,0,0.1);
    background:linear-gradient(#FFF000, #DDD000);
    background:-o-linear-gradient(#FFF000, #DDD000);
    background:-ms-linear-gradient(#FFF000, #DDD000);
    background:-moz-linear-gradient(#FFF000, #DDD000);
    background:-webkit-linear-gradient(#FFF000, #DDD000);
    padding:3px;

    }

    input:hover, textarea:hover {
    color:#fff;
    background:#123123;
    text-decoration:underline;
    }
    </style>

    '''
webstr = '''

    <a href=https://github.com/Noobay/Hackita/tree/master/AppEngine>check git out!</a>(Project)
    <a href=https://github.com/depasonico/bywaf-owasp>based on this</a>(WAFterpreter)
        <form action="/index" method="post">
            Enter a command <input name="cmd" type="text" />
            <input value="cmd" type="submit" />
        </form>

    '''

out_textarea = '{0} <pre> <textarea readonly> {1} </textarea>  </pre> '
out_normal = '{0} <pre>  {1}  </pre>'


@get('/index')# or @route('/')
def web_input():
    return webstr


@post('/index')
def proc_input():
    w_input = request.forms.get('cmd')


    args = w_input.split(' ', 1)
    try:
        newfunc = getattr(wafterpreter, 'do_'+args[0])
        if len(args) < 2:
            args.append("")
        else:
            pass

    except AttributeError:
        return 'no such function exists'
    except IndexError:
        return 'try another function'

    newfunc(args[1])
    wafterpreter.save_history_db(w_input)

    return out_textarea.format(style+webstr, waf_out.getvalue())






#set up wafterperter
inp    = sys.stdin
waf_out = StringIO()
wafterpreter = WAFterpreter(stdin=inp, stdout=waf_out)

#run the webapp
app = default_app()

