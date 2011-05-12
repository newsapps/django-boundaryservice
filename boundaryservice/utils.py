from django.conf import settings

def get_site_url_root():
    domain = getattr(settings, 'MY_SITE_DOMAIN', 'localhost')
    protocol = getattr(settings, 'MY_SITE_PROTOCOL', 'http')
    port     = getattr(settings, 'MY_SITE_PORT', '')
    url = '%s://%s' % (protocol, domain)
    if port:
        url += ':%s' % port
    return url
