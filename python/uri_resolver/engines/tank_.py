import urllib
import os

from urlparse import urlparse
from .base import BaseResolver

import sys
sys.path.append('/mnt/ala/mav/2018/jobs/s118/config/pipeline/production/install/core/python')

import sgtk

PATH_VAR_REGEX =r'[$]{1}[A-Z_]*'
VERSION_REGEX = r'v[0-9]{3}'
ZMQ_NULL_RESULT = "NOT_FOUND"
VERBOSE = True


class TankResolver(BaseResolver):

    """
    This is super hacky!  It should be replaced with a ShotgunResolver
    rather than scraping the file system.
    Also variables other than version should eventually be supported.
    """
    _name = 'tank'

    @property
    @classmethod
    def name(cls):
        return cls._name

    def validate(self, uri):
        pass

    def __init__(cls):
        cls.authenticate()

    @classmethod
    def authenticate(self):
        # Import the ShotgunAuthenticator from the tank_vendor.shotgun_authentication
        # module. This class allows you to authenticate either interactively or, in this
        # case, programmatically.
        from tank_vendor.shotgun_authentication import ShotgunAuthenticator

        # Instantiate the CoreDefaultsManager. This allows the ShotgunAuthenticator to
        # retrieve the site, proxy and optional script_user credentials from shotgun.yml
        cdm = sgtk.util.CoreDefaultsManager()

        # Instantiate the authenticator object, passing in the defaults manager.
        authenticator = ShotgunAuthenticator(cdm)

        # Create a user programmatically using the script's key.
        user = authenticator.create_script_user(
            api_script="toolkit_user",
            api_key="ebd86c2232481aac5ea589bd11831926af90cb937c59f05b50860a112bff2524"
        )

        # print "User is '%s'" % user

        # Tells Toolkit which user to use for connecting to Shotgun.
        sgtk.set_authenticated_user(user)

    @classmethod
    def uri_to_filepath(cls, uri):
        """
        uri: "tank:/maya_publish_asset_cache_usd?Step=model&Task=model&asset_type=setPiece&version=latest&Asset=building01"

        returns filepath: "/mnt/ala/mav/2018/jobs/s118/assets/setPiece/building01/model/model/caches/usd/building01_model_model_usd.v028.usd"
        """

        cls.authenticate()


        print "uri resolver received: %s\n" % uri

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

        # avoid hardcoding path, but requires us to be in a sg context::
        # eng = sgtk.platform.current_engine()
        # tk = eng.tank

        # hard code path - works anywhere:
        tk = sgtk.tank_from_path("/mnt/ala/mav/2018/jobs/s118/config/pipeline/production/install/core/python")

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

                print "tank uri resolver returning: %s\n" % ZMQ_NULL_RESULT
                return ZMQ_NULL_RESULT

            else:
                print "tank uri resolver returning: %s\n" % publishes[-1]
                return publishes[-1]


    @classmethod
    def filepath_to_uri(cls, filepath, version_flag="latest"):
        """
        filepath: "/mnt/ala/mav/2018/jobs/s118/assets/setPiece/building01/model/model/caches/usd/building01_model_model_usd.v028.usd"

        returns uri: "tank:/maya_publish_asset_cache_usd?Step=model&Task=model&asset_type=setPiece&version=latest&Asset=building01"
        """
        cls.authenticate()

        eng = sgtk.platform.current_engine()
        tk = eng.tank
        templ = tk.template_from_path(filepath)

        if not templ:
            return

        fields = templ.get_fields(filepath)
        fields['version'] = version_flag

        #print fields
        query = urllib.urlencode(fields)
        uri = '%s:/%s?%s' % (cls._name, templ.name, query)
        return uri

    @classmethod
    def fields_to_uri(cls, templ_name, fields):

        # Generate url query ?key=val&key2=val2
        query = urllib.urlencode(fields)

        # Construct our tank uri
        uri = '%s:/%s?%s' % (cls._name, templ_name, query)

        return uri

    @staticmethod
    def is_tank_asset(filepath, tk):
        cls.authenticate()

        templ = tk.template_from_path(filepath)
        return True if templ else False
