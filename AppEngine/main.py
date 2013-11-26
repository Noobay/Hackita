#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
from bottle import request, route,template, get, post, default_app
from bywaf import WAFterpreter
import os,sys
from cStringIO import StringIO

webstr = '''
    <a href=https://github.com/depasonico/bywaf-owasp>check git out! (yay, a pun!)</a>
        <form action="/index" method="post">
            Input: <input name="input" type="text" />
            <input value="input" type="submit" />
        </form>
    '''
@get('/index')# or @route('/')
def web_input():
    return webstr


@post('/index')
def proc_input():
    w_input = request.forms.get('input')


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

    return '{0} <plaintext> {1}'.format(webstr, waf_out.getvalue())






#set up wafterperter
inp    = sys.stdin
waf_out = StringIO()
wafterpreter = WAFterpreter(stdin=inp, stdout=waf_out)

#run the webapp
app = default_app()

