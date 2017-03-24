from urlparse import urlparse

import engines


def uri_to_filepath(uri):
    tokens = urlparse(uri)
    scheme = tokens.scheme
    engine = _get_engine(scheme)
    return engine.uri_to_filepath(uri)


def filepath_to_uri(filepath, scheme):
    engine = _get_engine(scheme)
    return engine.filepath_to_uri(filepath, scheme)


def _get_engine(name):
    engine = engines.registered.get(name)
    if not engine:
        raise RuntimeError("Engin %s was not registered" % name)
    return engine
