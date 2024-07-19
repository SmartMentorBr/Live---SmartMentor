#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
import unittest
import sys, os
import urllib2
sys.path.append('./tests/interface_tests/lib')
from selenium import webdriver
import subprocess
import os.path


ROOT = 'http://localhost:8001'

class FunctionalTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.web2py = start_web2py_server()
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(1)


    @classmethod
    def tearDownClass(self):
        self.browser.close()
        self.web2py.kill()

    def get_response_code(self, url):
        handler = urllib2.urlopen(url)
        return handler.getcode()


def start_web2py_server():
    print os.path.curdir
    return subprocess.Popen([
        "python", "../../web2py.py",  'runserver', '-a "passwd"', '-p 8001'
    ]
    )


def run_functional_tests(pattern=None):
    print('running tests')
    if(pattern is None):
        tests = unittest.defaultTestLoader.discover("./tests/interface_tests")
    else:
        pattern_with_globs = "*%s" % (pattern,)
        tests = unittest.defaultTestLoader.discover(
            './tests/interface_tests', pattern=pattern_with_globs)

    runner = unittest.TextTestRunner()
    runner.run(tests)


if __name__ == "__main__":
    if(len(sys.argv) == 1):
        run_functional_tests()
    else:
        run_functional_tests(pattern=sys.argv[1])

