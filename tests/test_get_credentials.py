#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
__author__ = 'E. S. Pereira'
__date = '30-10-2015'

import unittest
import sys
from gluon.globals import Request, Session, Storage, Response

path = os.path.join(request.folder,'tests/interface_tests/lib')
if not path in sys.path: sys.path.append(path)
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


execfile("./applications/" + app + "/controllers/default.py")

class Test_get_credentials(unittest.TestCase):

    @classmethod
    def setUpClass(self):


        request = Request(globals())
        session = Session()
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(10)
        self.username = 'relattoweb'
        self.passwd = 'relatto2014'
        resetDB()


    @classmethod
    def tearDownClass(self):
        self.browser.close()

    def test_flowSession(self):
        resp = get_credentials()
        #print(resp['authorise_url'])

        self.browser.get(resp['authorise_url'])
        self.browser.find_element_by_id('Email').send_keys(self.username)
        self.browser.find_element_by_id('next').click()
        self.browser.find_element_by_id('Passwd').send_keys(self.passwd)
        self.browser.find_element_by_id('signIn').click()
        self.browser.find_element_by_id('submit_approve_access').click()

        self.assertIsNotNone(session.flow)
