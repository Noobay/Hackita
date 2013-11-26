# coding=utf-8

'''
cowsay plugin for wafterperter
written by: Adar Grof
For your entertainment
'''


intro = '''
 _____
/  __ \\
| /  \/  ___  __      __ ___   __ _  _   _
| |     / _ \ \ \ /\ / // __| / _` || | | |
| \__/\| (_) | \ V  V / \__ \| (_| || |_| |
 \____/ \___/   \_/\_/  |___/ \__,_| \__, |
                                      __/ |
                                     |___/ '''
options = {'Option': ['Value', 'Defualt', 'Required', 'Description']}

animals = {'cow':'''
         \   ^__^
          \  (oo)\_______
             (__)\       )\/\/
                 ||----w |
                 ||     ||    ''',

           'doge': '''
        ░░░░░░░░░▄░░░░░░░░░░░░░░▄░░░░
        ░░░░░░░░▌▒█░░░░░░░░░░░▄▀▒▌░░░
        ░░░░░░░░▌▒▒█░░░░░░░░▄▀▒▒▒▐░░░
        ░░░░░░░▐▄▀▒▒▀▀▀▀▄▄▄▀▒▒▒▒▒▐░░░
        ░░░░░▄▄▀▒░▒▒▒▒▒▒▒▒▒█▒▒▄█▒▐░░░
        ░░░▄▀▒▒▒░░░▒▒▒░░░▒▒▒▀██▀▒▌░░░
        ░░▐▒▒▒▄▄▒▒▒▒░░░▒▒▒▒▒▒▒▀▄▒▒▌░░
        ░░▌░░▌█▀▒▒▒▒▒▄▀█▄▒▒▒▒▒▒▒█▒▐░░
        ░▐░░░▒▒▒▒▒▒▒▒▌██▀▒▒░░░▒▒▒▀▄▌░
        ░▌░▒▄██▄▒▒▒▒▒▒▒▒▒░░░░░░▒▒▒▒▌░
        ▀▒▀▐▄█▄█▌▄░▀▒▒░░░░░░░░░░▒▒▒▐░
        ▐▒▒▐▀▐▀▒░▄▄▒▄▒▒▒▒▒▒░▒░▒░▒▒▒▒▌
        ▐▒▒▒▀▀▄▄▒▒▒▄▒▒▒▒▒▒▒▒░▒░▒░▒▒▐░
        ░▌▒▒▒▒▒▒▀▀▀▒▒▒▒▒▒░▒░▒░▒░▒▒▒▌░
        ░▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒░▒░▒░▒▒▄▒▒▐░░
        ░░▀▄▒▒▒▒▒▒▒▒▒▒▒░▒░▒░▒▄▒▒▒▒▌░░
        ░░░░▀▄▒▒▒▒▒▒▒▒▒▒▄▄▄▀▒▒▒▒▄▀░░░
        ░░░░░░▀▄▄▄▄▄▄▀▀▀▒▒▒▒▒▄▄▀░░░░░
        ░░░░░░░░░▒▒▒▒▒▒▒▒▒▒▀▀░░░░░░░░
                                     ''',
           'chick': '''
                       .---.
            _ /     ' .---.
            >|  o    `     `\\
            ` \       .---._ '._ ,
               '-.;         /`  /'
                  \    '._.'   /
                   '.        .'
                     `";--\_/
                     _/_   |
                  -'`/  .--;--
                    '    .'        '''

}

bubbles = {'default': ['_', '-'], 'decorated': ['/_\\', '/-\\']}


def do_cowsay(line):
    if not line:
        return
    if len(line.split()) < 1:
        app.stdout.write('not enough parameters')
        return
    if len(line.split()) > 3 and line.split()[0] == '$':
        animal, bubble, line = line[1:].split(None, 3)
    else:
            animal = 'cow'
            bubble = 'default'
    spacer = ' '*(9-len(line))
    app.stdout.write('\n'+spacer+' '+bubbles[bubble][0]*len(line)+'\n')
    app.stdout.write(spacer+'<'+line+'>'+'\n')
    app.stdout.write(spacer+' '+bubbles[bubble][1]*len(line))
    app.print_line(animals[animal])
