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

PATH_VAR_REGEX =r'[$]{1}[A-Z_]*'
VERSION_REGEX = r'v[0-9]{3}'
ZMQ_NULL_RESULT = "NOT_FOUND"
VERBOSE = False


class _Resolver(object):
    path_var_regex = r'[$]{1}[A-Z_]*'
    version_regex = r'v[0-9]{3}'
    zmq_null_result = "NOT_FOUND"
    verbose = False
    _instance = None

    def __init__(self):
        self.proj = os.getenv('DEFAULT_PROJECT')
        self.sgtk = None
        self.sg_info = None
        self.tank = None

        self.setup()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(_Resolver, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def setup(self):
        self.load_sg_info()

        # the order of the following calls matters

        # first import sgtk:
        self.import_sgtk()

        # sg authentication must happen after sgtk import:
        self.authenticate()

        # tank object comes last:
        self.tank_ = self.load_tank()

    def load_tank(self):
        """

        Returns:

        """
        proj_name = self.proj or os.getenv('DEFAULT_PROJECT')
        proj_install = self.sg_info['install']
        proj = proj_install[proj_name]
        self.tank = self.sgtk.tank_from_path(proj)

    def import_sgtk(self):
        """

        Returns:

        """
        sgtk_location = os.environ['SHARED_TANK_PATH']
        sys.path.append(sgtk_location)
        import sgtk
        self.sgtk = sgtk

    def load_sg_info(self):
        sg_info_file = os.environ['SHOTGUN_INFO']

        with open(sg_info_file) as f:
            self.sg_info = json.load(f)

    def authenticate(self):
        """

        Args:
            sgtk:

        Returns:

        """

        if self.sgtk.get_authenticated_user():
            if not self.sgtk.get_authenticated_user().are_credentials_expired():
                print "Credentials already exist."
                return

        print "Authenticating credentials."

        # Import the ShotgunAuthenticator from the tank_vendor.shotgun_authentication
        # module. This class allows you to authenticate either interactively or, in this
        # case, programmatically.
        from tank_vendor.shotgun_authentication import ShotgunAuthenticator

        # Instantiate the CoreDefaultsManager. This allows the ShotgunAuthenticator to
        # retrieve the site, proxy and optional script_user credentials from shotgun.yml
        cdm = self.sgtk.util.CoreDefaultsManager()

        # Instantiate the authenticator object, passing in the defaults manager.
        authenticator = ShotgunAuthenticator(cdm)

        # Create a user programmatically using the script's key.
        user = authenticator.create_script_user(
            api_script="toolkit_user",
            api_key=os.getenv('SG_API_KEY')
        )

        # Tells Toolkit which user to use for connecting to Shotgun.
        self.sgtk.set_authenticated_user(user)


def uri_to_filepath(uri):
    """

    Args:
        uri:

    Returns:

    """
    _resolver = _Resolver()

    # this is necessary for katana - for some reason katana ships with it's own
    # modified version of urlparse which only works for some protocols, so switch
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
    platform = fields.get('platform')

    # can't remember if it's necessary to do this, now we have a shared install?
    if proj:
        if proj != _resolver.proj:
            _resolver.proj = proj
            _resolver.load_tank()

    template_path = _resolver.tank.templates[template]

    if VERBOSE:
        print("tank uri resolver found sgtk template: %s\n" % template_path)

    if not version:
        return None

    result = ""
    fields_ = {}
    for key in fields:
        if key == 'version':
            continue
        fields_[key] = fields[key]

    publishes = _resolver.tank.paths_from_template(template_path, fields_)

    if len(publishes) == 0:
        return ZMQ_NULL_RESULT

    publishes.sort()

    if VERBOSE:
        print "tank uri resolver found publishes: %s\n" % publishes

    # asset time was specified
    if asset_time:
        asset_time = float(asset_time)
        while len(publishes) > 0:
            latest = publishes.pop()
            latest_time = os.path.getmtime(latest)

            # handle rounding issues - apparently this happens:
            if (abs(latest_time - asset_time) < 0.01) or (latest_time < asset_time):
                result = latest

        if not result:
            result = ZMQ_NULL_RESULT

    # no asset time was specified - get the latest
    else:
        result = publishes[-1]

    if platform == 'windows':
        # currently we assume the turret server is running on linux, so
        # the retried path will be a linux one

        win_platform = _resolver.sg_info['platform']['windows']
        lin_platform = _resolver.sg_info['platform']['linux']

        # there may be a better way to do this, without accessing a private member?
        windows_root = template_path._per_platform_roots[win_platform]
        linux_root = template_path._per_platform_roots[lin_platform]

        result = result.replace(linux_root, windows_root)
        result = result.replace('/', '\\')

    return result


def filepath_to_uri(filepath, version_flag="latest", proj=""):
    """

    Args:
        filepath:
        version_flag:
        proj:

    Returns:

    """
    _resolver = _Resolver()

    templ = _resolver.tank.template_from_path(filepath)

    if not templ:
        print "Couldnt find template"
        return

    fields = templ.get_fields(filepath)
    fields['version'] = version_flag

    install_ = _resolver.sg_info['install']

    for key in install_:
        value = install_[key]
        if filepath.startswith(value):
            proj = key
            break

    # can't remember if it's necessary to do this, now we have a shared install?
    if proj != _resolver.proj:
        _resolver.proj = proj
        _resolver.load_tank()

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
    templ = tk.template_from_path(filepath)
    return True if templ else False

