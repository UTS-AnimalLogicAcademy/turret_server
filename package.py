# -*- coding: utf-8 -*-
name = 'uri_resolver'

version = '0.0.8'

authors = ['daniel.flood']

requires = ['pyzmq']

build_requires = ['python']

def commands():
    env.PYTHONPATH.append('{this.root}/python')

uuid = '521166cd-725a-402c-a424-e68d24c448fc'

