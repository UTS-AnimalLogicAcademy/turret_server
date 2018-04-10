# -*- coding: utf-8 -*-
name = 'zmq_server'

version = '0.0.2'

authors = ['wen.tan',
           'ben.skinner']

tools = ['start_uri_server']

requires = ['pyzmq',
            'uri_resolver']

build_requires = ['python']

def commands():
    env.PYTHONPATH.append('{root}/python')
    env.ZMQ_SERVER = '{root}/python'
    env.PATH.append('{root}/bin')

uuid = '3f17be78-3dd3-4a36-879c-0cf898e088ea'
