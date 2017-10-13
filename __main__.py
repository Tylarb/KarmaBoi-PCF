#!/usr/bin/env python

import KarmaBoi
import os
import dbinit


print('This is a Karma Boi')

if not os.path.exists(dbinit.DB_PATH + 'karmadb'):
    print("No database exists \n  Creating databases for the first time")
    dbinit.create_users_table()

name = input('please provide a name:\n')
print('You\'ve chosen ' + name)
karmaInput = input('please add or subtract karma\n')


if karmaInput == '++':
    karma = KarmaBoi.karma_add(name)
elif karmaInput == '--':
    karma = KarmaBoi.karma_sub(name)
else:
    karma = KarmaBoi.karma_ask(name)

if karma is None:
    print(name + ' has no karma')
else:
    print(name + ' now has ' + str(karma) + ' points of karma' )
