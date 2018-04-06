# -*- coding: utf-8 -*-
name = 'uri_resolver'

version = '0.0.9'

authors = ['daniel.flood']

tools = ['start_uri_server']

requires = ['pyzmq']

build_requires = ['python']

def commands():
    env.PYTHONPATH.append('{root}/python')
    env.PATH.append('{root}/bin')
    

uuid = '521166cd-725a-402c-a424-e68d24c448fc'

