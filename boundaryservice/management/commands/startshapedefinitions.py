import os
from optparse import make_option
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError



class Command(BaseCommand):
    """
    Create a new definitions.py file to configure shapefiles to be loaded into the database.
    
    Fails if the file already exists. Requires that the SHAPEFILES_DIR setting is configured.
    
    You can force the creation of a new file by adding the `-f` or `--force`` flag.
    
    Example usage::
    
        $ python manage.py startshapedefinitions
    
    """
    help = 'Create a new definitions.py file to configure shapefiles to be loaded into the database.'
    custom_options = (
        make_option('-f', '--force',
            action='store_true', dest='force',
            help='Force the creation of a new defintions.py, even if it already exists.'
        ),
    )
    option_list = BaseCommand.option_list + custom_options

    def handle(self, *args, **options):
        shp_dir = getattr(settings, 'SHAPEFILES_DIR', 'data/shapefiles')
        if not os.path.exists(shp_dir):
            raise CommandError("The shapefiles directory does not exist. Create data/shapefiles/ or set SHAPEFILES_DIR in settings.py.")
        def_path = os.path.join(shp_dir, "definitions.py")
        if os.path.exists(def_path) and not options.get("force"):
            raise CommandError("Sorry, %s already exists." % def_path)
        outfile = open(def_path, "w")
        outfile.write(BOILERPLATE)
        outfile.close()
        self.stdout.write('Created definitions.py in %s\n' % shp_dir)


BOILERPLATE = """from datetime import date

SHAPEFILES = {
    # This key should be the plural name of the boundaries in this set
    'City Council Districts': {
        # Path to a shapefile, relative to /data/shapefiles
        'file': 'city_council_districts/Council Districts.shp',
        # Generic singular name for an boundary of from this set
        'singular': 'City Council District',
        # Should the singular name come first when creating canonical identifiers for this set?
        'kind_first': False,
        # Function which each feature wall be passed to in order to extract its "external_id" property
        # The utils module contains several generic functions for doing this
        'ider': None,
        # Function which each feature will be passed to in order to extract its "name" property
        'namer': None,
        # Authority that is responsible for the accuracy of this data
        'authority': 'Tyler GIS Department',
        # Geographic extents which the boundary set encompasses
        'domain': 'Tyler',
        # Last time the source was checked for new data
        'last_updated': date(2011, 5, 14),
        # A url to the source of the data
        'href': 'http://www.smithcountymapsite.org/webshare/data.html',
        # Notes identifying any pecularities about the data, such as columns that were deleted or files which were merged
        'notes': '',
        # Encoding of the text fields in the shapefile, i.e. 'utf-8'. If this is left empty 'ascii' is assumed
        'encoding': '',
        # SRID of the geometry data in the shapefile if it can not be inferred from an accompanying .prj file
        # This is normally not necessary and can be left undefined or set to an empty string to maintain the default behavior
        'srid': ''
    }
}"""
