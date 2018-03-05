import os
from urlparse import urlparse
# import uritools
import re

from .base import BaseResolver


PATH_VAR_REGEX =r'[$]{1}[A-Z_]*'
VERSION_REGEX = r'v[0-9]{3}'

WINDOWS_PROJ_ROOT = "A:/jobs"
LINUX_PROJ_ROOT = "/mnt/ala/jobs"

class FilesystemResolver(BaseResolver):

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

    @classmethod
    def uri_to_filepath(cls, uri):

        uri_tokens = urlparse(uri)
        path = uri_tokens.path
        path_vars = re.findall(PATH_VAR_REGEX, path)

        for var in path_vars:

            if var not in ['$VERSION']:
                continue

            dir = os.path.split(path)[0]
            file_ = os.path.split(path)[-1]
            file_tokens = re.split(PATH_VAR_REGEX, file_)

            versions = os.listdir(dir)
            version_ints = []

            for version in versions:
                try:
                    version_str = re.findall(VERSION_REGEX, version)[0]
                    resolved_file_tokens = re.split(version_str, version)

                    if file_tokens != resolved_file_tokens:
                        continue

                    version_ints.append(int(version_str[1::]))
                except:
                    continue


            version_ints.sort()
            latest = version_ints[-1]
            latest_str = 'v%03d' % latest

            path = path.replace('$VERSION', latest_str)

        if path.startswith('$PROJ_ROOT'):
            if os.name == 'posix':
                path = path.replace('$PROJ_ROOT', LINUX_PROJ_ROOT)
            if os.name == 'nt':
                path = path.replace('$PROJ_ROOT', WINDOWS_PROJ_ROOT)

        return path

    # "filesystem:/mnt/ala/jobs/s171/assets/Prop/machineDebri003/model/publish/caches/machineDebri003.$VERSION.abc"
    # "filesystem:$PROJ_ROOT/s171/assets/Prop/machineDebri003/model/publish/caches/machineDebri003.$VERSION.abc"

    @classmethod
    def validate(self, uri):
        # no validation for now - should probably check that the pardir path exists?
        pass

    @classmethod
    def filepath_to_uri(cls, filepath):
        match = re.findall(VERSION_REGEX, filepath)

        if not match:
            return "{0}:{1}".format(cls._name, filepath)

        version = match[0]
        return "{0}:{1}".format(cls._name, filepath.replace(version, '$VERSION'))
