from django.core.urlresolvers import reverse, resolve
from django.http import Http404
from django.shortcuts import get_object_or_404

from boundaryservice.models import Boundary

def external_id_redirects(request, api_name, resource_name, slug, external_id):
    """
    Fake-redirects /boundary-set/slug/external_id paths to the proper canonical boundary path.
    """
    if resource_name != 'boundary-set':
        raise Http404 

    boundary = get_object_or_404(Boundary, set__slug=slug, external_id=external_id)
    
    # This bit of hacky code allows to execute the resource view as the canonical url were hit, but without redirecting
    # Note that the resource will still have correct, canonical 'resource_uri' attribute attached
    canonical_url = reverse('api_dispatch_detail', kwargs={'api_name': api_name, 'resource_name': 'boundary', 'slug': boundary.slug})
    view, args, kwargs = resolve(canonical_url)

    return view(request, *args, **kwargs)

