# -*- coding: utf-8 -*-
name = 'uri_resolver'

version = '0.0.10'

authors = ['daniel.flood',
           'ben.skinner']

tools = ['start_uri_server']

requires = ['pyzmq']

build_requires = ['python']

def commands():
    env.PYTHONPATH.append('{root}/python')
    env.URI_SERVER = '{root}/python/uri_zmq'
    env.PATH.append('{root}/bin')
    

uuid = '521166cd-725a-402c-a424-e68d24c448fc'

