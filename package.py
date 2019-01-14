# -*- coding: utf-8 -*-

name = 'turret_server'

version = '1.0.0'

authors = ['wen.tan',
           'ben.skinner',
           'daniel.flood']

requires = ['pyzmq']

build_requires = ['python']

def commands():
    env.PATH.append('{root}/bin')
    env.TURRET_SERVER.set('{root}/bin/launch-turret-server.sh')
    env.PYTHONPATH.append('{root}/python')
