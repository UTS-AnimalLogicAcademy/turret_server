from abc import ABCMeta, abstractmethod, abstractproperty


class BaseResolver(object):

    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        pass

    @abstractmethod
    def uri_to_filepath(self, uri):
        pass

    @abstractmethod
    def filepath_to_uri(self, filepath, scheme):
        pass



