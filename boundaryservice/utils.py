from django.conf import settings


def get_site_url_root():
    domain = getattr(settings, 'MY_SITE_DOMAIN', 'localhost')
    protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'http')
    port = getattr(settings, 'MY_SITE_PORT', '')
    url = '%s://%s' % (protocol, domain)
    if port:
        url += ':%s' % port
    return url

#
# Utility methods for transforming shapefile columns into useful
# representations
#


class static_namer():
    """
    Name features with a single, static name.
    """
    def __init__(self, name):
        self.name = name

    def __call__(self, feature):
        return self.name


class index_namer():
    """
    Name features with a static prefix, plus an iterating value.
    """
    def __init__(self, prefix):
        self.prefix = prefix
        self.i = 0

    def __call__(self, feature):
        out = '%s%i' % (self.prefix, self.i)
        self.i += 1
        return out


class simple_namer():
    """
    Name features with a joined combination of attributes, optionally passing
    the result through a normalizing function.
    """
    def __init__(self, attribute_names, seperator=' ', normalizer=None):
        self.attribute_names = attribute_names
        self.seperator = seperator
        self.normalizer = normalizer

    def __call__(self, feature):
        attribute_values = map(str, map(feature.get, self.attribute_names))
        name = self.seperator.join(attribute_values).strip()

        if self.normalizer:
            normed = self.normalizer(name)
            if not normed:
                raise ValueError('Failed to normalize \"%s\".' % name)
            else:
                name = normed

        return name
