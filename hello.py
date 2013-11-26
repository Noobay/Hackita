# encoding=utf-8
from string import maketrans
from bottle import run, route, template, request


# hello world function
@route('/hello world')
def helloworld():
    print('hello world')


# hello world with input
@route('/fa/<foo>')
def fa(foo):
   return template('<b>hello {{name}}</b>', name=foo)


# X bottles of beer on the wall
@route('/beers/<bottle_num>')
def beers(bottle_num=100):
    template('{{a}} bottles of beer on the wall, {{a}} bottles of beer. \nTake one down, pass it around, {{b}} bottles of beer on the wall...', a=str(bottle_num), b=str(bottle_num-1))
    beers(bottle_num-1) if bottle_num > 1 else None


@route('/gematria/<word>')
def gematria_dict(word):
    word = unicode(word, 'utf-8')
    gematria = {
u'א':	1,
u'ב'	:2,
u'ג'	:3,
u'ד'	:4,
u'ה'    :5,
u'ו'	:6,
u'ז'	:7,
u'ח'	:8,
u'ט'	:9,
u'י'	:10,
u'כ'	:20,
u'ל'	:30,
u'מ'	:40,
u'נ'	:50,
u'ס'	:60,
u'ע'	:70,
u'פ'	:80,
u'צ'	:90,
u'ק'	:100,
u'ר'	:200,
u'ש'	:300,
u'ת'	:400,
u'ך'    :500,
u'ם'    :600,
u'ן'    :700,
u'ף'    :800,
u'ץ'    :900
}


    value = 0
    for char in word:
        if char in gematria:
            value += gematria[char]
    return 'equals {0} in gematria'.format(value)


@route('/palin/<word>')
# see if word is a plaindrome, ignore punctuation and loops
def is_palindrome(word):
    word = word.translate(maketrans('{},.[]()', '        '))
    if(word == word[::-1]):
        return template('<b>{{sp}} is a palindrome</b>', sp=word)
    else:
        return template('<b>{{sp}} is not a palindrome</b>', sp=word)

def mult_list(number):
    pass


run(host='localhost', port=8080)


