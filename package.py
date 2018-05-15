# -*- coding: utf-8 -*-
name = 'uri_resolver'

version = '0.0.19'

authors = ['daniel.flood',
           'ben.skinner']

build_requires = ['python']

tools = ['uri_resolver']

def commands():
    env.PYTHONPATH.append('{root}/python')

    env.PATH.append('{root}/bin')
    #env.PYTHONPATH.append("{root}/python")
    
    #env.USD_UTILS_PATH.set("{root}/python")

uuid = '521166cd-725a-402c-a424-e68d24c448fc'

