#
# Copyright 2019 University of Technology, Sydney
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
# to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
#   * The above copyright notice and this permission notice shall be included in all copies or substantial portions of
#     the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import json
import sys
import urllib
import os
from urlparse import urlparse

from . import sg_authenticate

PATH_VAR_REGEX =r'[$]{1}[A-Z_]*'
VERSION_REGEX = r'v[0-9]{3}'
ZMQ_NULL_RESULT = "NOT_FOUND"
VERBOSE = False

PROJ = ""
AUTHENTICATED = False
SGTK = False

# Make sure these environment variables are set:
#
# Path to a json file, with a dict of {projName: projPath}
# $PROJ_MAP
#
# Optional environment variables:
#
# if you don't store the project name in the URI:
# $DEFAULT_PROJECT


def uri_to_filepath(uri):
    """

    Args:
        uri:

    Returns:

    """

    # this is necessary for katana - for some reason katana ships with it's own
    # mangled version of urlparse which only works for some protocols, so switch
    # to http
    if uri.startswith('tank://'):
        uri = uri.replace('tank://', 'http:/')
    elif uri.startswith('tank:/'):
        uri = uri.replace('tank:/', 'http:/')

    uri_tokens = urlparse(uri)
    query = uri_tokens.query
    path_tokens = uri_tokens.path.split('/')

    # support legacy URIs, i.e. no project in path:
    if len(path_tokens) == 2:
        proj = os.environ['DEFAULT_PROJECT']
        template = path_tokens[1]
    else:
        proj = path_tokens[1]
        template = path_tokens[2]

    query_tokens = query.split('&')
    fields = {}

    for field in query_tokens:
        key, value = field.split('=')
        fields[key] = value

    version = fields.get('version')
    asset_time = fields.get('time')

    # project is specified in URI
    if proj:
        global PROJ
        if proj != PROJ:
            # cache proj value to global
            PROJ = proj

    global SGTK
    if not SGTK:
        SGTK = sg_authenticate.import_sgtk()

    global AUTHENTICATED
    if not AUTHENTICATED:
        sg_authenticate.authenticate(SGTK)
        AUTHENTICATED = True

    tank = get_tank()
    template_path = tank.templates[template]

    if VERBOSE:
        print("tank uri resolver found sgtk template: %s\n" % template_path)

    if version:
        fields_ = {}
        for key in fields:
            if key == 'version':
                continue
            fields_[key] = fields[key]

        publishes = tank.paths_from_template(template_path, fields_)

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


def filepath_to_uri(filepath, version_flag="latest", proj=""):
    """

    Args:
        filepath:
        version_flag:
        proj:

    Returns:

    """

    if not proj:
        proj = os.environ['DEFAULT_PROJECT']

    global PROJ
    if proj != PROJ:
        PROJ = proj

    global SGTK
    if not SGTK:
        SGTK = sg_authenticate.import_sgtk()

    global AUTHENTICATED
    if not AUTHENTICATED:
        sg_authenticate.authenticate(SGTK)
        AUTHENTICATED = True

    tank = get_tank()
    templ = tank.template_from_path(filepath)

    if not templ:
        print "Couldnt find template"
        return

    fields = templ.get_fields(filepath)
    fields['version'] = version_flag
    query = urllib.urlencode(fields)
    uri = 'tank:/%s/%s?%s' % (proj, templ.name, query)
    return uri


def fields_to_uri(templ_name, fields):
    """

    Args:
        templ_name:
        fields:

    Returns:

    """
    query = urllib.urlencode(fields)
    uri = 'tank:/%s?%s' % (templ_name, query)
    return uri


def is_tank_asset(filepath, tk):
    """

    Args:
        filepath:
        tk:

    Returns:

    """
    global SGTK
    if not SGTK:
        SGTK = sg_authenticate.import_sgtk()

    global AUTHENTICATED
    if not AUTHENTICATED:
        sg_authenticate.authenticate(SGTK)
        AUTHENTICATED = True

    sg_authenticate.authenticate(SGTK)
    templ = tk.template_from_path(filepath)
    return True if templ else False


def get_tank():
    """

    Returns:

    """
    global SGTK
    if not SGTK:
        SGTK = sg_authenticate.import_sgtk()

    proj_map_file = os.environ['PROJ_MAP']

    with open(proj_map_file) as f:
        proj_map = json.load(f)

    proj = proj_map[PROJ]

    tank = SGTK.tank_from_path(proj)
    return tank
