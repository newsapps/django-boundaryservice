from tastypie.throttle import CacheThrottle

class AnonymousThrottle(CacheThrottle):
    """
    Anonymous users are throttled, but those with a valid API key are not.
    """
    def should_be_throttled(self, identifier, **kwargs):
        if not identifier.startswith('anonymous_'):
            return False

        return super(AnonymousThrottle, self).should_be_throttled(identifier, **kwargs)
