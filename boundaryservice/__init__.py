import logging
import os
import re

logger = logging.getLogger(__name__)

registry = {}
_basepath = '.'

def register(name, **kwargs):
    kwargs['file'] = os.path.join(_basepath, kwargs.get('file', ''))
    registry[name] = kwargs

def autodiscover(base_dir):
    global _basepath
    definition_file_re = re.compile(r'definitions?\.py$')
    for (dirpath, dirnames, filenames) in os.walk(base_dir):
        _basepath = dirpath
        for filename in filenames:
            if definition_file_re.search(filename):
                logger.debug(filename)
                execfile(os.path.join(dirpath, filename))

def attr(name):
    return lambda f: f.get(name)

def _title_string(name):
    return name.title()

def title_attr(name):
    attr_getter = attr(name)
    return lambda f: _title_string(attr_getter(f))