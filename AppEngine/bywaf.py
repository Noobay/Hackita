#!/usr/bin/env python2

# ---------------------------------------------------
# bywaf.py
# ---------------------------------------------------

""" Bywaf. """

# standard Python libraries
import argparse
from cmd import Cmd
import sys
import string
import imp # for loading other modules
import os
from google.appengine.api import users
from google.appengine.ext import db
import urllib2 as ulib


# path to the root of the plugins directory
DEFAULT_PLUGIN_PATH = "./"

# history file name
DEFAULT_HISTORY_FILENAME = "bywaf-history.txt"

# DB entity class
class User(db.Model):
            user = db.StringProperty(required=False)
            history = db.StringProperty(required=False)
            date = db.DateProperty(auto_now_add=True)
            time = db.IntegerProperty()

# Interactive shell class
class WAFterpreter(Cmd):

   def __init__(self, completekey='tab', stdin=None, stdout=None):
      Cmd.__init__(self, completekey, stdin, stdout)

      # base wafterpreter constants
      self.intro = "Welcome to Bywaf"
      self.base_prompt = "Bywaf"
      self.set_prompt('') # set the prompt
      self.delegate_input_handler = None # no delegated input by default

      # currently loaded plugins, loaded & selected with he "use" command.
      # is a dictionary of { "plugin_name" : loaded_module_object }
      self.plugins = {}

      # dictionary of global variable names and values
      self.global_options = {}



      self.current_plugin = None
      self.current_plugin_name = ''

      #set up db user
      self.order = 0
      # create host information database



   # ----------- Overriden Methods ------------------------------------------------------
   #
   # The following methods from Cmd have been overriden to provide more functionality
   #
   # ------------------------------------------------------------------------------------

   # override Cmd.emptyline() so that it does not re-issue the last command by default
   def emptyline(self):
       return

   # override exit from command loop to say goodbye
   def postloop(self):
        self.print_line('Goodbye')

   # override Cmd.getnames() to return dir(), and not
   # dir(self.__class__).  Otherwise, get_names() doesn't return the
   # names of dynamically-added do_* commands
   def get_names(self):
       return dir(self)

   # override completenames() to give an extra space (+' ') for completed command names
   # and to better matches bash's completion behavior
   def completenames(self, text, line, begidx, endidx, level=1):
        dotext = 'do_'+text
        return [a[3:]+' ' for a in self.get_names() if a.startswith(dotext)]

   # override Cmd.onecmd() to enable user to background a task
   def onecmd(self, _line):

        # call the delegation function first, if it has been defined
        if self.delegate_input_handler:
            self.delegate_input_handler(_line)
            return

        # flag variable
        exec_in_background = False
        line = _line.strip()

        # ignore comment lines
        if line.startswith('#'):
            return

        # if the user only specified a number, then show the results of that backgrounded task
        if line.isdigit():
            self.do_result(line)
            return

        # set the backgrounding flag if the line ends with &
        if line.endswith('&'):
            exec_in_background = True
            line = _line[:-1]

        # extract command and its arguments from the line
        cmd, arg, line = self.parseline(line)
        self.lastcmd = line

        # if the line is blank, return self.emptyline()
        if not cmd:
            return self.emptyline()

        # quit on EOF
        elif cmd in ['EOF', 'quit', 'exit']:
            self.lastcmd = ''
            return 1 # 0 keeps WAFterpreter going, 1 quits it

        # else, process the command
        else:
            try:
                func = getattr(self, 'do_' + cmd)
            except AttributeError:
                self.print_line('command "{}" not found'.format(cmd))
                return # return self.default(line)

            # list of commands for the currently-selected plugin
            command_names = []
            if self.current_plugin:
                command_names = self.current_plugin.commands

            func(arg)
            ret = 0 # 0 keeps WAFterpreter going, 1 quits it

            return ret

   # ----------- API and Utility Methods ----------------------------------------------
   #
   # These methods are exposed to the plugins and may be overriden by them.
   #
   #-----------------------------------------------------------------------------------


   # utility method to autocomplete filenames.
   # Code adapted from http://stackoverflow.com/questions/16826172/filename-tab-completion-in-cmd-cmd-of-python
   # I added "level", which is the level of command at which text is being completed.
   # level 1:  >command te<tab>   <-- text being completed here
   # level 2:  >command subcommand te<tab>  <-- text being completed here
   def filename_completer(self, text, line, begidx, endidx, level=1, root_dir='./'):

      arg = line.split()[level:]

      if not arg:
          completions = os.listdir(root_dir)
      else:
          dir, part, base = arg[-1].rpartition('/')
          if part == '':
              dir = './'
          elif dir == '':
              dir = '/'

          completions = []
          for f in os.listdir(dir):
              if f.startswith(base):
                  if os.path.isfile(os.path.join(dir,f)):
                      completions.append(f)
                  else:
                      completions.append(f+'/')

      return completions


   # set input handler: all input will be redirected to the input handler 'delegate_func'
   def set_delegate_input_handler(self, delegate_func):

       # set the delegated input handler
       self.delegate_input_handler = delegate_func


   # restore Bywaf normal input handling functionality
   def unset_delegate_input_handler(self):

       # restore old prompt
       self.set_prompt(self.current_plugin_name)  # fix this

       # cancel further input delegation
       self.delegate_input_handler = None

   # set an option's value.  Called by do_set()
     # set an option's value.  Called by do_set()
   def set_option(self, name, value):

       # retrieve the option (it's a tuple)
       _value, _defaultvalue, _required, _descr = self.current_plugin.options[name]

       # defer first to the specific setter callback, if it exists
       try:
           setter_func = getattr(self.current_plugin, 'set_'+name)
           setter_func(name, value)

       # specific option setter callback doesn't exist,  so do a straight assignment
       except AttributeError:

#           self.print_line('raised AttributeError trying to call a set_{}'.format(name))
           # construct a new option tuple and set the option to it
           try:
               self.current_plugin.set_default(name, value)
           except AttributeError:
#               self.print_line('raised AttributeError trying to call a set_default({})'.format(name))

               # default option setter doesn't exist; fall back to a direct assignment
               self.current_plugin.options[name] = value, _defaultvalue, _required, _descr



     # physically load a module (called from do_import)
     # implementation adapted from http://stackoverflow.com/questions/301134/dynamic-module-import-in-python
   def _load_module(self, filepath):

       py_mod = None

       # extract module's name and extension from filepath
       mod_name,file_ext = os.path.splitext(os.path.split(filepath)[-1])

       # if it is a precompiled module, use the precompiled loader
       if file_ext.lower() == '.pyc':
           try:
               py_mod = imp.load_compiled(mod_name, filepath)
           except Exception as e:
               raise Exception('Could not load precompiled plugin module: {}'.format(e))

       # else just try to load it with the standard loader
       else:

           py_mod = imp.load_source(mod_name, filepath)
           try:
               pass
           except Exception as e:
               raise Exception('Could not load plugin module: {}'.format(e))

       # verify that this module has the necessary Bywaf infrastructure
       if not hasattr(py_mod, "options"):
           raise Exception("options dictionary not found")

       # return the loaded module
       return mod_name, py_mod

   # set the prompt to the given plugin name
   def set_prompt(self, plugin_name):
       try:   # can fail if no plugin is loaded (i.e. plugin_name=="")
           self.prompt = self.base_prompt + '/' + plugin_name + '>'
       except:
           self.prompt = self.base_prompt + '>'

   # retrieve command history
   # code adapted from pymotw.com/2/readline/
   def get_history_items(self):
       '''  return [ readline.get_history_item(i)
                for i in xrange(1, readline.get_current_history_length() + 1)
                ]'''

   # try to write history to disk.  It is the caller's responsibility to handle exceptions
   def save_history(self, filename):
       '''readline.write_history_file(filename)'''

   # read history in, if it exists  It is the caller's responsibility to handle exceptions
   def load_history(self, filename):
       '''    readline.read_history_file(filename)'''

   # clear command history
   def clear_history(self):
      ''' readline.clear_history()'''


   # ----------- Command & Command Completion methods ------------------------------------------


   # load plugin module given its file path, and set it as the current plugin
   def do_use(self, _filepath):
       """Load a module given the module path"""

       filepath = _filepath.strip()


       try:
           new_module_name, new_module = self._load_module(filepath)
       except Exception as e:
           self.print_line('Could not load module {}: {}'.format(filepath,e))
           return

       # if this plugin has already been loaded, notify user.
       # this will revert any changes they made to the options
       if self.current_plugin_name == new_module_name:
           self.print_line('Import:  Overwriting already loaded module "{}"'.format(new_module_name))

       # give the new module access to other modules
       new_module.app = self

       # remove currently selected plugin's functions from the Cmd command list
       if self.current_plugin:
           for _command in self.current_plugin.commands:
               command = _command.__name__
               if hasattr(self, command):  delattr(self, command)
               if hasattr(self, 'help_'+command):  delattr(self, 'help_'+command[5:])
               if hasattr(self, 'complete_'+command):  delattr(self, 'complete_'+command[10:])

       # register with our list of modules (i.e., insert into our dictionary of modules)
       self.plugins[new_module_name] = new_module

       commands = [f for f in dir(new_module) if f.startswith('do_')]
       self.plugins[new_module_name].commands = commands

       # give plugin a link to its own path
       self.plugins[new_module_name].plugin_path = filepath

       # set current plugin
       # and change the prompt to reflect the plugin's name
       self.set_prompt(new_module_name)
       self.current_plugin_name = new_module_name
       self.current_plugin = new_module


       # add module's functions to the Cmd command list
       for command_name in new_module.commands:

           # register the command
           # it is a tuple of the form (function, string)
           command_func = getattr(new_module, command_name)
           setattr(self, command_name, command_func)

           # try and register its optional help function, if one exists
           try:
               helpfunc = getattr(new_module, 'help_' + command_name[3:])
               setattr(self, helpfunc.__name__, helpfunc)
           except AttributeError:  # help_ not found
               pass

           # try and register its optional completion function, if one exists
           try:
               completefunc = getattr(new_module, 'complete_' + command_name[3:])
               setattr(self, completefunc.__name__, completefunc)
           except AttributeError:  # complete__ not found
               pass
           #print intro message
           try:
               self.print_line(new_module.intro)
           except Exception as e:
               self.print_line(e)

   def complete_use(self,text,line,begin_idx,end_idx):
       return self.filename_completer(text, line, begin_idx, end_idx, root_dir=self.global_options['PLUGIN_PATH'])


   def do_gset(self, args):
       """set a global variable.  This command takes the form 'gset VARNAME VALUE'."""

       (key,value) = string.split(args, maxsplit=1)
       self.global_options[key] = value

       self.print_line('{} => {}'.format(key, value))

   # completion function for the do_gset command: return available global option names
   def complete_gset(self,text,line,begin_idx,end_idx):
       option_names = [opt+' ' for opt in self.global_options.keys() if opt.startswith(text)]
       return option_names

   def do_gshow(self, args):
       """Show global variables."""

       # construct the format string:  function name, description
       format_string = '{:<20.20} {}'

       # self.print_line the header
       self.stdout.write(format_string.format('Global Option', 'Value'))
       self.stdout.write(format_string.format(*["-"*20] * 2))

       for k in sorted(self.global_options.keys()):
           self.print_line(format_string.format(k, self.global_options[k]))

   # completion function for the do_gset command: return available global option names
   def complete_gshow(self, text, line,begin_idx,end_idx):
       option_names = [opt+' ' for opt in self.global_options.keys() if opt.startswith(text)]
       return option_names

   def set(self, name, value):
       """set a plugin's local variable.  This command takes the form 'set VARNAME VALUE'."""
       self.set_option(name, value)
       self.print_line('{} => {}'.format(name, value))

   #sets plugin parameters, takes the format of 'set NAME_1=VALUE_1 NAME_2=VALUE_2 ...'

   #sets plugin parameters, takes the format of 'set NAME_1=VALUE_1 NAME_2=VALUE_2 ...'
   def do_set(self,arg):
       """set a plugin's local variable.  This command takes the form 'set VARNAME=VALUE VARNAME2=VALUE2 ... VARNAME=VALUEN.  Values can be enclosed in single- and double-quotes'."""

       # line taken from http://stackoverflow.com/questions/16710076/python-split-a-string-respect-and-preserve-quotes
       items = re.findall(r'(?:[^\s,"]|"(?:\\.|[^"])*")+', arg)

       if not self.current_plugin:
           self.print_line('no plugin selected; you must first select a plugin with the "use" command.')
           return

       if  len(items)==0:
           self.print_line('no option set')
           return

       for i in items:
           key, value = string.split(i, '=', maxsplit=1)  # only split up to the first '='

           # remove double- and single-quotes from the split string, if it has any
           if (value.startswith('\'') and value.endswith('\'')) or (value.startswith('"') and value.endswith('"')):
               value = value[1:-1]

           # set the option
           try:
               self.print_line('{} => {}'.format(key, value))
               self.set_option(key, value)
           except AttributeError:
               self.print_line('Unknown plugin option "{}"'.format(key))

   # completion function for the do_set command: return available option names
   def complete_set(self,text,line,begin_idx,end_idx):
       option_names = [opt+' ' for opt in self.current_plugin.options.keys() if opt.startswith(text)]
       return option_names

   def do_show(self, args):
       """display local vars for this plugin"""

       # if no plugin is currently selected
       if not self.current_plugin:
           self.stdout.write('No plugin currently selected')
           return

       SHOW_COMMANDS = False
       SHOW_OPTIONS = False
       params = args.split()
       output_string = []

       # show all by default
       if params == []:
           params.append('all')

       if params[0] in ('options', 'all'):

               if len(params)<2:
                   options_list = self.current_plugin.options.keys()
               else:
                   options_list = params[1:]

               # construct the format string:  left-aligned, space-padded, minimum.maximum
               # name, value, defaultvalue, required, description
               format_string = '{:<15.15} {:<15.15} {:<15.15} {:<15.15} {:<15.30}'

               # construct header string
               output_string.append('\n\n')
               output_string.append(format_string.format('Option', 'Value', 'Default Value', 'Required', 'Description'))
               output_string.append(format_string.format(*['-'*15] * 5))

               # construct table of values
               try:
                   for name in options_list:
                       output_string.append(format_string.format(name, *self.current_plugin.options[name]))
               except KeyError:
                   self.stdout.write("Error, no such option")
                   return

       if params[0] in ('commands','all'):

               # show all options if no option name was given
#               try:
#                   commands_list = params[1:]
#               except IndexError:
#                   commands_list = self.current_plugin.commands

               _command_list = self.current_plugin.commands
               if len(params)<2:
                   commands_list = _command_list
               else:  # note: the if clause closes this comprehension to insecure lookups
                   commands_list = ['do_' + c for c in params[1:]]# if 'do_'+c in _command_list]

               # get the option names from the rest of the parameters.

               # construct the format string:  left-aligned, space-padded, minimum.maximum
               # name, value, defaultvalue, required, description
               format_string = '{:<20.20} {}'

               # construct header
               output_string.append('\n\n')
               output_string.append(format_string.format('Command', 'Description'))
               output_string.append(format_string.format(*['-'*20] * 2))

               try:
                   for c in commands_list:
                       cmd = getattr(self.current_plugin, c)
                       output_string.append(format_string.format(cmd.__name__[3:], cmd.__doc__))


               except AttributeError:
                   self.stdout.write("Error, no such command")
                   return

               output_string.append('\n')


       # display
       self.stdout.write('\n'.join(output_string))




   # utility function for completing against a list of matches,
   # given a list of words that have been inputted, a matchlist to match the word against,
   # and the level of the command
   def simplecompleter(self, words, matchlist, level):

      # user has not yet strted entering their choice
      if len(words)==level:
           return matchlist

      # user has entered a partial word
      else:
           partial_word = words[level]
           return [opt + ' ' for opt in matchlist if opt.startswith(partial_word)]


   # completion function for the do_set command: return available option names
   def complete_show(self,text,line,begin_idx,end_idx):

     words = line.split()

     first_level = ['commands', 'options', 'all']

     # find out if this is first- or second-level completion:
     # FIXME:  Make this generic and put it into an API helper function
     # first level completion: we see either one word, OR two words and the second is only partially completed.  Complete the subcommand.
     if len(words)==1 or (len(words)==2 and words[1] not in first_level):
         option_names = [opt+' ' for opt in first_level if opt.startswith(text)]
         return option_names
     # second level completion: we see two words, the second fully completed. Complete the option or command name.
     else:
         # return a list of plugin commands
         if words[1]=='commands':
             # construct new list of command names without "do_"
             cmds = [i[3:] for i in self.current_plugin.commands]
             return self.simplecompleter(words, cmds, level=2)

         # return a list of plugin options
         elif words[1]=='options':
             opts = self.current_plugin.options.keys()
             return self.simplecompleter(words, opts, level=2)

   def do_load(self, line):
       try:
           webpage = ulib.urlopen(line)
           page_code = webpage.read()
           if 'cgi-bin' in page_code:
               page_code = page_code.replace('cgi-bin', line+'/'+'cgi-bin')
           if 'src="/' in page_code:
               page_code = page_code.replace('src="/', 'src="'+line)
           self.stdout.write('</textarea> {0} <textarea>'.format(page_code))
       except Exception as e:
           self.stdout.write(e)
           self.stdout.write('\n'+'operation failed')


   def do_shell(self, line):
       """Execute shell commands"""
       output = os.popen(line).read()
       self.self.print_line(output)

   def do_clear(self, line):
       """clears stdout"""
       self.stdout.truncate(0)
       self.stdout.seek(0)

   def do_clearhist(self, line):
       """clear history"""
       db.delete(db.Query())

   def save_history_db(self, entry):
       self.order += 1
       user = User(user=users.get_current_user(), history=entry, time=self.order)
       user.put()

   def load_history_db(self):
      result = db.Query(User)
      result.order('time')
      lista = [entry.history for entry in result]

      self.stdout.write('\n'.join(lista))
      self.stdout.write('\n')


   def clear_history_db(self):
        pass

   def do_history(self, line):
       """show command history."""
       self.load_history_db()


   def print_line(self, line):
       self.stdout.write(line)
       self.stdout.write('\n')
       self.stdout.flush()

#prevents exceptions from bringing down the app
#and offers options to handle the exception.
def interpreter_loop():
    try:
        wafterpreter.cmdloop()
        sys.exit(0)

    # handle an exception
    except Exception as e:

        wafterpreter.print_line('\nerror encountered, continue[Any-Key], show stack trace and continue[SC], show stack trace and quit[S]')

        # python2/3 compatibility check
        try:
            input = raw_input
        except NameError:
            pass

        # ask user how they want to handle the exception
        answer = input()

        # show stack trace and quit
        if answer == 'S' or answer == 's':
            raise(e)

        # show stack trace and continue
        elif answer == 'SC' or answer == 'sc':
            wafterpreter.print_line("failed")

        #present the error briefly
        else:
            wafterpreter.print_line('{}\n'.format(e))

    #we don't want to show the user the welcome message again.
    wafterpreter.intro = ''
    interpreter_loop()

#---------------------------------------------------------------
#
# Main function
#
#---------------------------------------------------------------


if __name__=='__main__':

    # parse arguments
    parser = argparse.ArgumentParser(description='Bypass web application firewalls')
    parser.add_argument('--input', dest='inputfilename', action='store', help='read input from a file')
    parser.add_argument('--script', dest='scriptfilename', action='store', help='execute a script and stay in wafterpreter')
    parser.add_argument('--out', dest='outfilename', action='store', help='redirect output to a file')
    parser.add_argument('--pluginpath', dest='plugin_path', action='store', help='specify the root plugin directory', default=DEFAULT_PLUGIN_PATH)
    parser.add_argument('--historyfilename', dest='history_filename', action='store', help='specify name of command history file', default=DEFAULT_HISTORY_FILENAME)
    args = parser.parse_args()

    # assign default input and output streams
    input = sys.stdin
    output = sys.stdout

    # set the input and output streams according to the user's request
    if args.inputfilename:
        try:
            input = open(args.inputfilename, 'rt')
        except IOError as e:
            print('Could not open input file: {}'.format(e))
            sys.exit(1)

    if args.outfilename:
        try:
            output = open(args.outfilename, 'rt')
        except IOError as e:
            print('Could not open output file: {}'.format(e))
            sys.exit(2)


    # initialize command interpreter
    wafterpreter = WAFterpreter(stdin=input, stdout=output)

    # automatically read history in, if it exists
    wafterpreter.global_options['HISTORY_FILENAME'] = args.history_filename
    try:
        wafterpreter.load_history(wafterpreter.global_options['HISTORY_FILENAME'])#DEFAULT_HISTORY_FILENAME)
    except IOError:
        pass

    # set default plugin root path...
    wafterpreter.global_options['PLUGIN_PATH'] = DEFAULT_PLUGIN_PATH

    # try to set root plugin path from environment variable
    try:
        wafterpreter.global_options['PLUGIN_PATH'] = os.environ['PLUGIN_PATH']
    except KeyError as e:
        pass

    # try to set root plugin path from command-line parameter
    try:
        wafterpreter.global_options['PLUGIN_PATH'] = args.plugin_path
    except KeyError as e:
        pass

    # verify that plugin path exists
    try:
        os.path.isdir(wafterpreter.global_options['PLUGIN_PATH'])
    except IOError as e:
        print('Error: could not find plugin path or invalid plugin path specified: {}'.format(e))


    # execute a script if the user specified one
    if args.scriptfilename:
        try:
            wafterpreter.do_script(args.scriptfilename)
        except IOError as e:
            print('Could not open script file: {}'.format(e))
            sys.exit(3)

    # begin accepting commands
    interpreter_loop()