import urllib
from urlparse import urlparse
from .base import BaseResolver

import tank


PATH_VAR_REGEX =r'[$]{1}[A-Z_]*'
VERSION_REGEX = r'v[0-9]{3}'
TANK_ROOT = '/mnt/ala/jobs'

#todo: get the project context from tank somehow...
PROJ = 's171'

class TankResolver(BaseResolver):

    """
    This is super hacky!  It should be replaced with a ShotgunResolver
    rather than scraping the file system.
    Also variables other than version should eventually be supported.
    """
    _name = 'filesystem'

    @property
    @classmethod
    def name(cls):
        return cls._name

    def validate(self, uri):
        pass

    @classmethod
    def uri_to_filepath(cls, uri):
        if uri.startswith('tank://'):
            uri.replace('tank://', 'tank:/')

        uri_tokens = urlparse(uri)
        query = uri_tokens.query
        path_tokens = uri_tokens.path.split('/')
        job = path_tokens[1]
        template = path_tokens[2]
        query_tokens = query.split('&')
        fields = {}

        tk = tank.tank_from_path('%s/%s' % (TANK_ROOT, job))
        template_path = tk.templates[template]

        for field in query_tokens:
            key, value = field.split('=')
            fields[key] = value

        version = fields.get('version')

        if version == 'latest':
            fields_ = {}
            for key in fields:
                if key == 'version':
                    continue
                fields_[key] = fields[key]

            publishes = tk.paths_from_template(template_path, fields_)
            versions = [template_path.get_fields(x).get('version') for x in publishes]
            versions.sort()
            latest = versions[-1]
            fields["version"] = latest

        publish = tk.paths_from_template(template_path, fields)

        if publish:
            return publish[0]


    @classmethod
    def filepath_to_uri(cls, filepath, scheme):
        tk = tank.tank_from_path("%s/%s" % (TANK_ROOT, PROJ))
        templ = tk.template_from_path(filepath)

        if not templ:
            return

        fields = templ.get_fields(filepath)
        fields['version'] = 'latest'
        query = urllib.urlencode(fields)
        uri = 'tank:/%s/%s?%s' % (PROJ, templ.name, query)

        return uri


def is_tank_asset(filepath):
    tk = tank.tank_from_path("%s/%s" % (TANK_ROOT, PROJ))
    templ = tk.template_from_path(filepath)
    return True if templ else False
