import urllib
from urlparse import urlparse
from .base import BaseResolver

import sys
sys.path.append('/mnt/ala/mav/2018/jobs/s118/config/pipeline/production/install/core/python')

import sgtk

PATH_VAR_REGEX =r'[$]{1}[A-Z_]*'
VERSION_REGEX = r'v[0-9]{3}'


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

    @classmethod
    def uri_to_filepath(cls, uri):
        """
        uri: "tank:/maya_publish_asset_cache_usd?Step=model&Task=model&asset_type=setPiece&version=latest&Asset=building01"

        returns filepath: "/mnt/ala/mav/2018/jobs/s118/assets/setPiece/building01/model/model/caches/usd/building01_model_model_usd.v028.usd"
        """

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
        #print version
        test = fields.get('Asset')
        #print test

        eng = sgtk.platform.current_engine()
        #tk = eng.tank
        tk = sgtk.tank_from_path("/mnt/ala/mav/2018/jobs/s118/config/pipeline/production/install/core/python")
        template_path = tk.templates[template]

        print(" ---- %s" % template_path)

        if version:
            fields_ = {}
            for key in fields:
                if key == 'version':
                    continue
                fields_[key] = fields[key]

            publishes = tk.paths_from_template(template_path, fields_)
            versions = [template_path.get_fields(x).get('version') for x in publishes]

            assets = [template_path.get_fields(x).get('Asset') for x in publishes]
            print(assets)
            if(len(assets) == 0):
                return ""

            versions.sort()

            print("Versions found: %s" % str(versions))
            #if not versions:                                                                                        #if version doesnt exist -> works if asset name
            #    return "INVALID INPUT"
            if(version.isdigit()):
                if(int(version) in versions):
                    latest = version
            else:
                latest = versions[-1]
                

            fields["version"] = int(latest)
            print(fields)

        publish = tk.paths_from_template(template_path, fields)

        if publish:
            return publish[0]

    @classmethod
    def filepath_to_uri(cls, filepath, version_flag="latest"):
        """
        filepath: "/mnt/ala/mav/2018/jobs/s118/assets/setPiece/building01/model/model/caches/usd/building01_model_model_usd.v028.usd"

        returns uri: "tank:/maya_publish_asset_cache_usd?Step=model&Task=model&asset_type=setPiece&version=latest&Asset=building01"
        """
        eng = sgtk.platform.current_engine()
        tk = eng.tank
        templ = tk.template_from_path(filepath)

        if not templ:
            return

        fields = templ.get_fields(filepath)
        fields['version'] = version_flag

        uri = fields_to_uri(templ.name, fields)

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
        templ = tk.template_from_path(filepath)
        return True if templ else False
