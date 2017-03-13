import os
import uritools
import re

from .base import BaseResolver


PATH_VAR_REGEX =r'[$]{1}[A-Z_]*'
VERSION_REGEX = r'v[0-9]{3}'

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

        uri_tokens = uritools.urisplit(uri)
        path = uri_tokens.getpath()
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

        return path

    @classmethod
    def filepath_to_uri(cls, filepath, scheme):
        version = re.findall(VERSION_REGEX, filepath)[0]
        return "{0}:{1}".format(scheme, filepath.replace(version, '$VERSION'))

