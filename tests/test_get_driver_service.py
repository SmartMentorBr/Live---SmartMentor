#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
__author__ = 'E. S. Pereira'
__date = '06-11-2015'

import unittest
from gluon.globals import Request, Session, Storage, Response
import os
path = os.path.join(request.folder,'tests/interface_tests/lib')
if not path in sys.path: sys.path.append(path)
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import time
execfile("./applications/" + app + "/controllers/default.py")

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


class Test_get_driver_service(unittest.TestCase):

    @classmethod
    def setUpClass(self):


        request = Request(globals())
        session = Session()
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(1)
        self.username = 'relattoweb'
        self.passwd = 'relatto2014'
        resetDB()
        self.code = getCode(self.browser, self.username, self.passwd)


    @classmethod
    def tearDownClass(self):
        self.browser.close()


    def test_filelist(self):
        request.vars['code'] = self.code
        oauth2callback()
        resp = get_driver_service()
        self.assertIsNotNone(resp)
