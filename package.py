# -*- coding: utf-8 -*-
# foo
# bar
# foo
# bar
# foo
# bar

name = 'uri_resolver'

version = '0.0.6'

authors = ['daniel.flood']

build_requires = ['python']
# not sure how to capture "tank" dependency?  i.e. not a rez package?

def commands():
    env.PYTHONPATH.append('{this.root}/python')

uuid = '521166cd-725a-402c-a424-e68d24c448fc'

