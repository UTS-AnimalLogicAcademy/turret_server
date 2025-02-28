# -*- coding: utf-8 -*-

name = 'turret_server'

version = '1.3.0'

authors = ['wen.tan',
           'ben.skinner',
           'daniel.flood',
           'jonah.newton']

requires = ['pyzmq-21.6', 'turret_resolver', 'python-3.7+']

def commands():
    env.PATH.append('{root}/bin')
    env.TURRET_SERVER.set('{root}/bin/turret-server-launcher.sh')
    env.TURRET_SRC.set('{root}/src')

    env.PYTHONPATH.append(env.TURRET_SRC)
