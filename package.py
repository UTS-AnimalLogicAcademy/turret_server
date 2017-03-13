# -*- coding: utf-8 -*-

name = 'uri_resolver'

version = '0.0.3'

authors = ['daniel.flood']

requires = ['uritools']

build_requires = ['python']

def commands():
    env.PYTHONPATH.append('{this.root}/python')

uuid = '521166cd-725a-402c-a424-e68d24c448fc'

