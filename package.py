# -*- coding: utf-8 -*-
name = 'zmq_server'

version = '0.0.4'

authors = ['wen.tan',
           'ben.skinner']

requires = ['pyzmq',
            'uri_resolver']

build_requires = ['python']

def commands():
    env.PYTHONPATH.append('{root}/python')
    env.PATH.append('{root}/python')
    env.PATH.append('{root}/bin')
#    env.TANK_ZMQ_SERVER.set('{root}/python/zmq_server.py')
    env.TANK_ZMQ_SERVER.set('{root}/bin/launch_zmq_server.sh')

uuid = '3f17be78-3dd3-4a36-879c-0cf898e088ea'
