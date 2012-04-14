import re

from django.contrib.gis.db import models
from django.contrib.gis.models import SpatialRefSys
from django.conf import settings

from boundaryservice.fields import ListField, JSONField
from boundaryservice import utils
from boundaryservice.utils import get_site_url_root

NAMERS = {'static': utils.static_namer,
          'index': utils.index_namer,
          'simple': utils.simple_namer}
NAMER_CHOICES = NAMERS.items()
NAMER_CHOICES.sort()

settings.SHAPEFILES_SUBDIR = getattr(settings, 'SHAPEFILES_SUBDIR',
                                     'shapefiles')


class SluggedModel(models.Model):
    """
    Extend this class to get a slug field and slug generated from a model
    field. We call the 'get_slug_text', '__unicode__' or '__str__'
    methods (in that order) on save() to get text to slugify. The slug may
    have numbers appended to make sure the slug is unique.
    """
    slug = models.SlugField(max_length=256)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.unique_slug()
        if self.slug == '':
            raise ValueError("Slug may not be blank [%s]" % str(self))
        super(SluggedModel, self).save(*args, **kwargs)

    def unique_slug(self):
        """
        Customized unique_slug function
        """
        if not getattr(self, "slug"):  # if it's already got a slug, do nothing
            from django.template.defaultfilters import slugify
            if hasattr(self, 'get_slug_text') and callable(self.get_slug_text):
                slug_txt = self.get_slug_text()
            elif hasattr(self, '__unicode__'):
                slug_txt = unicode(self)
            elif hasattr(self, '__str__'):
                slug_txt = str(self)
            else:
                return
            slug = slugify(slug_txt)

            itemModel = self.__class__
            # the following gets all existing slug values
            allSlugs = set(sl.values()[0]
                           for sl in itemModel.objects.values("slug"))
            if slug in allSlugs:
                counterFinder = re.compile(r'-\d+$')
                counter = 2
                slug = "%s-%i" % (slug, counter)
                while slug in allSlugs:
                    slug = re.sub(counterFinder, "-%i" % counter, slug)
                    counter += 1

            setattr(self, "slug", slug)

    def fully_qualified_url(self):
        return get_site_url_root() + self.get_absolute_url()


class BoundarySet(SluggedModel):
    """
    A set of related boundaries, such as all Wards or Neighborhoods.
    """
    name = models.CharField(max_length=64, unique=True,
        help_text='Category of boundaries, e.g. "Community Areas".')
    singular = models.CharField(max_length=64,
        help_text='Name of a single boundary, e.g. "Community Area".')
    kind_first = models.BooleanField(
        help_text='If true, boundary display names will be "kind name" (e.g. '
        'Austin Community Area), otherwise "name kind" (e.g. 43rd Precinct).')
    authority = models.CharField(
        max_length=256,
        help_text='The entity responsible for this data\'s accuracy, e.g. '
        '"City of Chicago".')
    domain = models.CharField(
        max_length=256,
        help_text='The area that this BoundarySet covers, e.g. "Chicago" or '
        '"Illinois".')
    last_updated = models.DateField(
        help_text='The last time this data was updated from its authority (but'
        ' not necessarily the date it is current as of).')
    href = models.URLField(blank=True,
        help_text='The url this data was found at, if any.')
    notes = models.TextField(
        blank=True,
        help_text='Notes about loading this data, including any '
        'transformations that were applied to it.')
    count = models.IntegerField(
        help_text='Total number of features in this boundary set.')
    metadata_fields = ListField(
        separator='|', blank=True,
        help_text='What, if any, metadata fields were loaded from the original'
        ' dataset.')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        """
        Print plural names.
        """
        return unicode(self.name)


class Boundary(SluggedModel):
    """
    A boundary object, such as a Ward or Neighborhood.
    """
    set = models.ForeignKey(
        BoundarySet, related_name='boundaries',
        help_text='Category of boundaries that this boundary belongs, e.g. '
        '"Community Areas".')
    kind = models.CharField(
        max_length=64,
        help_text='A copy of BoundarySet\'s "singular" value for purposes of '
        'slugging and inspection.')
    external_id = models.CharField(
        max_length=64,
        help_text='The boundaries\' unique id in the source dataset, or a '
        'generated one.')
    name = models.CharField(
        max_length=192, db_index=True,
        help_text='The name of this boundary, e.g. "Austin".')
    display_name = models.CharField(
        max_length=256,
        help_text='The name and kind of the field to be used for display '
        'purposes.')
    metadata = JSONField(
        blank=True,
        help_text='The complete contents of the attribute table for this '
        'boundary from the source shapefile, structured as json.')
    shape = models.MultiPolygonField(
        srid=4269,
        help_text='The geometry of this boundary in EPSG:4269 projection.')
    simple_shape = models.MultiPolygonField(
        srid=4269,
        help_text='The geometry of this boundary in EPSG:4269 projection and '
        'simplified to 0.0001 tolerance.')
    centroid = models.PointField(
        srid=4269,
        null=True,
        help_text='The centroid (weighted center) of this boundary in '
        'EPSG:4269 projection.')

    objects = models.GeoManager()

    class Meta:
        ordering = ('kind', 'display_name')
        verbose_name_plural = 'Boundaries'

    def __unicode__(self):
        """
        Print names are formatted like "Austin Community Area"
        and will slug like "austin-community-area".
        """
        return unicode(self.display_name)


class PointSet(SluggedModel):
    """
    A set of related points, such as all bus stops or polling places.
    """
    name = models.CharField(max_length=64, unique=True,
        help_text='Category of points, e.g. "Bus Stops".')
    singular = models.CharField(max_length=64,
        help_text='Name of a single point, e.g. "Bus Stop".')
    kind_first = models.BooleanField(
        help_text='If true, point display names will be "kind name" (e.g. Bus '
        'Stop 43), otherwise "name kind" (e.g. 43rd Precinct Polling Place).')
    authority = models.CharField(
        max_length=256,
        help_text='The entity responsible for this data\'s accuracy, e.g. '
        '"City of Chicago".')
    domain = models.CharField(
        max_length=256,
        help_text='The area that this PointSet covers, e.g. "Chicago" or '
        '"Illinois".')
    last_updated = models.DateField(
        help_text='The last time this data was updated from its authority (but'
        ' not necessarily the date it is current as of).')
    href = models.URLField(blank=True,
        help_text='The url this data was found at, if any.')
    notes = models.TextField(
        blank=True,
        help_text='Notes about loading this data, including any '
        'transformations that were applied to it.')
    count = models.IntegerField(
        help_text='Total number of features in this point set.')
    metadata_fields = ListField(
        separator='|', blank=True,
        help_text='What, if any, metadata fields were loaded from the original'
        ' dataset.')

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        """
        Print plural names.
        """
        return unicode(self.name)


class Point(SluggedModel):
    """
    A point object, such as a bus stop or polling place.
    """
    set = models.ForeignKey(
        PointSet, related_name='points',
        help_text='Category of points that this point belongs, e.g. '
        '"Bus Stops".')
    kind = models.CharField(
        max_length=64,
        help_text='A copy of PointSet\'s "singular" value for purposes of '
        'slugging and inspection.')
    external_id = models.CharField(
        max_length=64,
        help_text='The points\' unique id in the source dataset, or a '
        'generated one.')
    name = models.CharField(
        max_length=192, db_index=True,
        help_text='The name of this point, e.g. "Community Center".')
    display_name = models.CharField(
        max_length=256,
        help_text='The name and kind of the field to be used for display '
        'purposes.')
    metadata = JSONField(
        blank=True,
        help_text='The complete contents of the attribute table for this '
        'point from the source shapefile, structured as json.')
    point = models.MultiPointField(
        srid=4269,
        null=True,
        help_text='The point in EPSG:4269 projection.')

    objects = models.GeoManager()

    class Meta:
        ordering = ('kind', 'display_name')
        verbose_name_plural = 'Points'

    def __unicode__(self):
        """
        Print names are formatted like "Bus Stop 42"
        and will slug like "bus-stop-42".
        """
        return unicode(self.display_name)


class Shapefile(models.Model):
    file = models.FileField(upload_to=settings.SHAPEFILES_SUBDIR)
    name = models.CharField(
        max_length=250,
        help_text='Generic name for boundaries from this set, e.g. "Counties"')
    singular = models.CharField(
        max_length=250,
        help_text='Generic singular name for a boundary from this set, e.g. '
        '"County"')
    kind_first = models.BooleanField(
        default=False,
        help_text='Should the singular name come first when creating canonical'
        ' identifiers for this set? e.g "Pretinct 80" vs "Tulsa County"')
    ider_namer = models.CharField(
        max_length=10, choices=NAMER_CHOICES, default='simple',
        help_text='Function which each feature wall be passed to in order to '
        'extract its "external_id" property. default: "simple"')
    ider_fields = models.CharField(
        max_length=250,
        help_text='Fields passed to name to create "external_id" property. '
        'Comma separate multiple fields. e.g. "OBJECTID"')
    name_namer = models.CharField(
        max_length=10, choices=NAMER_CHOICES, default='simple',
        help_text='Function which each feature wall be passed to in order to '
        'extract its "name" property. default: "simple"')
    name_fields = models.CharField(
        max_length=250,
        help_text='Fields passed to name to create "name" property. Comma '
        'seperate multiple fields. e.g. "NAME"')
    authority = models.CharField(
        max_length=250, blank=True,
        help_text='Authority responsible for the accuracy of this data.')
    domain = models.CharField(
        max_length=250, blank=True,
        help_text="Geographic extents which the boundary set encompasses")
    last_updated = models.DateField(
        blank=True, null=True,
        help_text="Last time the source was checked for new data")
    href = models.URLField(
        blank=True, help_text="A url to the source of the data")
    notes = models.TextField(
        blank=True,
        help_text='Notes identifying any pecularities about the data, such as '
        'columns that were deleted or files which were merged')
    encoding = models.CharField(
        max_length=50, blank=True,
        help_text='Encoding of the text fields in the shapefile, i.e. "utf-8".'
        ' If this is left empty "ascii" is assumed')
    srid_choices = [(s.srid, '%s - %s' % (s.srid, s.name)) for s in
                    SpatialRefSys.objects.order_by('srid')]
    srid = models.IntegerField(
        blank=True, null=True, choices=srid_choices,
        help_text='SRID of the geometry data in the shapefile if it can not be'
        ' inferred from an accompanying .prj file. This is normally not '
        'necessary and can be left undefined or set to an empty string to '
        'maintain the default behavior')
    simplification = models.DecimalField(
        max_digits=10, decimal_places=8, default=0.0001, blank=True, null=True,
        help_text='Simplification tolerance to use when creating the '
        'simple_geometry column for this shapefile, larger numbers create '
        'polygons with fewer points.')

    def __unicode__(self):
        return unicode(self.name)
