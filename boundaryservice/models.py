import re

from django.contrib.gis.db import models

from boundaryservice.fields import ListField, JSONField
from boundaryservice.utils import get_site_url_root

class BoundarySet(models.Model):
    """
    A set of related boundaries, such as all Wards or Neighborhoods.
    """
    slug = models.SlugField(max_length=200, primary_key=True)

    name = models.CharField(max_length=64, unique=True,
        help_text='Category of boundaries, e.g. "Community Areas".')
    singular = models.CharField(max_length=64,
        help_text='Name of a single boundary, e.g. "Community Area".')
    kind_first = models.BooleanField(
        help_text='If true, boundary display names will be "<kind> <name>" (e.g. Austin Community Area), otherwise "<name> <kind>" (e.g. 43rd Precinct).')
    authority = models.CharField(max_length=256,
        help_text='The entity responsible for this data\'s accuracy, e.g. "City of Chicago".')
    domain = models.CharField(max_length=256,
        help_text='The area that this BoundarySet covers, e.g. "Chicago" or "Illinois".')
    hierarchy = models.CharField(max_length=2, blank=True,
        choices=( ('F', 'Federal'),
                  ('P', 'Provincial'),
                  ('M', 'Municipal'),
                  ('O', 'Other')))
    last_updated = models.DateField(
        help_text='The last time this data was updated from its authority (but not necessarily the date it is current as of).')
    href = models.URLField(blank=True,
        help_text='The url this data was found at, if any.')
    notes = models.TextField(blank=True,
        help_text='Notes about loading this data, including any transformations that were applied to it.')
    count = models.IntegerField(
        help_text='Total number of features in this boundary set.')
    metadata_fields = ListField(separator='|', blank=True,
        help_text='What, if any, metadata fields were loaded from the original dataset.')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name

class Boundary(models.Model):
    """
    A boundary object, such as a Ward or Neighborhood.
    """
    boundaryset = models.ForeignKey(BoundarySet, related_name='boundaries',
        help_text='Category of boundaries that this boundary belongs, e.g. "Community Areas".')
    slug = models.SlugField(max_length=200)
    external_id = models.CharField(max_length=64,
        help_text='The boundaries\' unique id in the source dataset, or a generated one.')
    name = models.CharField(max_length=192, db_index=True,
        help_text='The name of this boundary, e.g. "Austin".')
    display_name = models.CharField(max_length=256,
        help_text='The name and kind of the field to be used for display purposes.')
    metadata = JSONField(blank=True,
        help_text='The complete contents of the attribute table for this boundary from the source shapefile, structured as json.')
    shape = models.MultiPolygonField(
        help_text='The geometry of this boundary in EPSG:4326 projection.')
    simple_shape = models.MultiPolygonField(
        help_text='The geometry of this boundary in EPSG:4326 projection and simplified to 0.0001 tolerance.')
    centroid = models.PointField(
        null=True,
        help_text='The centroid (weighted center) of this boundary in EPSG:4326 projection.')
    
    objects = models.GeoManager()

    class Meta:
        unique_together = (('slug', 'set'))

    def __unicode__(self):
        return self.display_name
