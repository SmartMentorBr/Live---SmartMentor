#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
__author__ = 'E. S. Pereira'
__date = '24-10-2015'

"""
Rodar testes de back-end contidos na pasta tests

FilenameDirectory -> DefaultTasksModel

Executar com:
>   python web2py.py -S relatto -M -R ./applications/relatto/testRunner.py

"""

import unittest
import glob
import sys
from copy import copy
from gluon.globals import Storage


suite = unittest.TestSuite()

app = "relatto"
locTestFiles = './applications/' + app + '/tests/'

# get all files with tests
test_files = glob.glob(locTestFiles + '*.py')

#test_files = [test_files[-1]]
if not len(test_files):
    raise Exception("No files found for app: " + app)

print('running tests')

for test_file in test_files:

    execfile(test_file, globals())
    classTestName =  str.capitalize(test_file.split("/")[-1][:-3])
    suite.addTest(unittest.makeSuite(globals()[classTestName]))

test_db = DAL('sqlite://testing.sqlite')
for tablename in db.tables:  # Copy tables!
    table_copy = [copy(f) for f in db[tablename]]
    test_db.define_table(tablename, *table_copy)


db=test_db

FAKEUSER = "username@xxxxxxxxxx"
FAKEPASS = 'password'
ROOT = 'http://localhost:8000/'
TESTEMODE = True

def resetDB():
    auth.settings.registration_requires_approval = False
    auth.settings.login_after_registration = True
    auth.settings.allow_basic_login = True
    for t in db.tables:
        db[t].truncate()
    db.commit()
    auth.user = Storage(dict(id=1))

    #password=db.auth_user.password.requires[0]('password')[0]
    #create a fake user
    #user_id = 1

    #db.auth_user.insert(first_name="Unittest",last_name="setUp",email=FAKEUSER,password=password)
    #add wanted membership (if needed)
    #auth.add_membership(auth.id_group("Manager"),user_id)
    #log user in
    #auth.login_bare(FAKEUSER, password)

def getCode(browser, username, passwd):
    resp = get_credentials()
    #print(resp['authorise_url'])

    browser.get(resp['authorise_url'])
    browser.find_element_by_id('Email').send_keys(username)
    browser.find_element_by_id('next').click()
    browser.find_element_by_id('Passwd').send_keys(passwd)
    browser.find_element_by_id('signIn').click()
    browser.find_element_by_id('submit_approve_access').click()

    url = browser.current_url
    while(url == browser.current_url):
        time.sleep(1)
        browser.find_element_by_id('submit_approve_access').click()
    code = browser.current_url.split('=')[-1]
    return code

unittest.TextTestRunner(verbosity=2).run(suite)
