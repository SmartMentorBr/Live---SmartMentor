#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
__author__ = 'E. S. Pereira'
__date = '14-11-2015'

import unittest
from gluon.globals import Request, Session, Storage, Response
import os
path = os.path.join(request.folder,'tests/interface_tests/lib')
if not path in sys.path: sys.path.append(path)
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

execfile("./applications/" + app + "/controllers/default.py")

class Test_get_analytics_service(unittest.TestCase):

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

    def test_get_analytics_service(self):
        request.vars['code'] = self.code
        oauth2callback()
        resp = get_analytics_service()
        self.assertIsNotNone(resp)
