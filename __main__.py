#!/usr/bin/env python

import KarmaBoi

print('This is a Karma Boi')

name = input('please provide a name:\n')
print('You\'ve chosen ' + name)


karma = KarmaBoi.karma_ask(name)
karma = KarmaBoi.karma_sub(name)
print(name + ' has ' + str(karma) + ' points of karma' )
