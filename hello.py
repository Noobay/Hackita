# encoding=utf-8

# hello world function
def h_world():
    print('hello world')

# helello world with input
def h_foo(foo):
    print('hello {}'.format(foo))

# X bottles of beer on the wall
def beer_ot_wall(bottle_num=100):
    print('{0} bottles of beer on the wall, {0} bottles of beer. \nTake one down, pass it around, {1} bottles of beer on the wall...'.format(str(bottle_num),str(bottle_num-1)))
    beer_ot_wall(bottle_num-1) if bottle_num > 1 else None

# see if word is a plaindrome
def is_palindrome(word):
    print word[len(word)-1: 2]

def gematria_dict(word):
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
    return value



if __name__ == '__main__':
    h_world()
    h_foo('worlds')
    beer_ot_wall(100)
    print gematria_dict(u"שלום")
    is_palindrome("wooooow")




