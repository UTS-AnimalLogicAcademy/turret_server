import urllib
import os
from urlparse import urlparse

from . import sg_authenticate

import sys
sys.path.append('/mnt/ala/mav/2018/jobs/s118/config/pipeline/production/install/core/python')
import sgtk

PATH_VAR_REGEX =r'[$]{1}[A-Z_]*'
VERSION_REGEX = r'v[0-9]{3}'
ZMQ_NULL_RESULT = "NOT_FOUND"
VERBOSE = False

TANK_PATH = "/mnt/ala/mav/2018/jobs/s118/config/pipeline/production/install/core/python"


def uri_to_filepath(uri):
    
    # this is necessary for katana - for some reason katana ships with it's own
    # mangled version of urlparse which only works for some protocols, super annoying
    if uri.startswith('tank://'):
        uri = uri.replace('tank://', 'http:/')
    elif uri.startswith('tank:/'):
        uri = uri.replace('tank:/', 'http:/')

    uri_tokens = urlparse(uri)
    query = uri_tokens.query
    path_tokens = uri_tokens.path.split('/')
    template = path_tokens[1]
    query_tokens = query.split('&')
    fields = {}

    for field in query_tokens:
        key, value = field.split('=')
        fields[key] = value

    version = fields.get('version')
    asset_time = fields.get('time')

    tk = sgtk.tank_from_path(TANK_PATH)

    template_path = tk.templates[template]

    if VERBOSE:
        print("tank uri resolver found sgtk template: %s\n" % template_path)

    if version:
        fields_ = {}
        for key in fields:
            if key == 'version':
                continue
            fields_[key] = fields[key]

        publishes = tk.paths_from_template(template_path, fields_)

        if len(publishes) == 0:
            return ZMQ_NULL_RESULT

        publishes.sort()

        if VERBOSE:
            print "tank uri resolver found publishes: %s\n" % publishes

        if asset_time:
            asset_time = float(asset_time)
            while len(publishes) > 0:
                latest = publishes.pop()
                latest_time = os.path.getmtime(latest)

                # handle rounding issues - apparently this happens:
                if (abs(latest_time - asset_time) < 0.01) or (latest_time < asset_time):
                    return latest

            return ZMQ_NULL_RESULT

        else:
            return publishes[-1]


def filepath_to_uri(filepath, version_flag="latest"):
    sg_authenticate.authenticate()

    tk = sgtk.tank_from_path(TANK_PATH)
    templ = tk.template_from_path(filepath)

    if not templ:
        print "Couldnt find template"
        return

    fields = templ.get_fields(filepath)
    fields['version'] = version_flag
    query = urllib.urlencode(fields)
    uri = '%s:/%s?%s' % (cls._name, templ.name, query)
    return uri


def fields_to_uri(templ_name, fields):
    query = urllib.urlencode(fields)
    uri = '%s:/%s?%s' % (cls._name, templ_name, query)
    return uri


def is_tank_asset(filepath, tk):
    sg_authenticate.authenticate()
    templ = tk.template_from_path(filepath)
    return True if templ else False
