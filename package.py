# -*- coding: utf-8 -*-
name = 'uri_resolver'

version = '0.0.9'

authors = ['daniel.flood', 
           'ben.skinner']

requires = ['pyzmq']

build_requires = ['python']

def commands():
    env.PYTHONPATH.append('{this.root}/python')

uuid = '521166cd-725a-402c-a424-e68d24c448fc'

