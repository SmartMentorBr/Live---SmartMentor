#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
__author__ = 'E. S. Pereira'

from functional_test import FunctionalTest, ROOT


class TestHomePage(FunctionalTest):
    def test_can_view_home_page(self):
        self.browser.get(ROOT+'/relatto/')
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('Easy, fast and transparent.', body.text)
