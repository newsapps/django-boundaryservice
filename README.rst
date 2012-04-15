=============================
The Boundary Service
=============================

The Boundary Service is a ready-to-deploy system for aggregating regional boundary data (from shapefiles) and republishing via a RESTful JSON API. It is packaged as a pluggable Django application so that it can be easily integrated into any project.

* `News Apps Boundary Service <https://github.com/newsapps/django-boundaryservice>`_: The inspiration and parent

Installation
============

Install and setup PostgreSQL, PostGIS, postgres-postgis, postgres-dev packages.

Next, create a PostgreSQL database, as the Boundary Service depends on PostGIS::
    
    $ DB=EXAMPLE_DB_NAME
    $ createdb -h localhost $DB
    $ createlang -h localhost plpgsql $DB

To spatially-enable the database, you must load PostGIS definitions files. You can use `locate` (Linux) or `mdfind` (OS X) to find these files::

    psql -h localhost -d $DB -f postgis.sql
    psql -h localhost -d $DB -f spatial_ref_sys.sql

Using pip::

    $ pip install git+git://github.com/tulsawebdevs/django-boundaryservice.git
    $ python manage.py syncdb

Add the following to INSTALLED_APPS in your settings.py

    ...
    'tastypie',
    'boundaryservice',
    ...

Add the following to your urls.py::

    (r'', include('boundaryservice.urls')),

Adding data
===========

To add data you will first need to add a shapefile and its related files (prj, dbf, etc.) to the data/shapefiles directory. Shapefiles and your definitions.py go into this folder. See the `hacktyler demo site <https://github.com/hacktyler/hacktyler-boundaryservice>`_ for a complete example. 

If you are choosing not to upload shapefiles via the Shapefile model, you can create your definitions file using a management command::

    $ python manage.py startshapedefinitions

You can load all definitions like so::

    $ python manage.py loadshapefiles

You may also override the default location by passing the "-d" flag to the command or setting SHAPEFILES_DIR in settings.py::

    $ python manage.py loadshapefiles -d data_dir

You can load only a specified shapefile with the "-o" flag::

    $ python manage.py loadshapefiles -o ShapeFileName

You can clear a particular shapefile from the database and reload it with the "-c" flag::

    $ python manage.py loadshapefiles -c ShapeFileName

Advice
======

**Definitions**

Of particular note amongst the defintion fields are the 'ider' and 'namer' properties. These should be assigned to functions which will be passed a feature's attributes as a dictionary. 'ider' should return a unique external id for the feature. (e.g. a district id number, geographic id code or any sequential primary key). Whenever possible these ids should be stable across revisions to the dataset. 'namer' should return a canonical name for the feature, not including its kind. (e.g. "Austin" for the Austin Community Area, "Chicago" for the City of Chicago, or #42 for Police Beat #42) A number of callable classes are defined in data/shapefiles/utils.py, which should mitigate the need to write custom functions for each dataset. 

**Namespacing**

As a matter of best practice when shapefiles have been acquired from government entities and other primary sources it is advisable not to modify them before loading them into the Boundary Service. (Thus why the Chicago neighborhoods shapefile is misspelled "Neighboorhoods".) If it is necessary to modify the data this should be noted in the 'notes' field of the shapefile's definitions.py entry.

Credits
=======

The Boundary Service is a product of the `News Applications team <http://blog.apps.chicagotribune.com>`_ at the Chicago Tribune. Core development was done by `Christopher Groskopf <http://twitter.com/onyxfish>`_ and `Ryan Nagle <http://twitter.com/ryannagle>`_. Modified by `Jeremy Satterfield <https://plus.google.com/103708024549095350813/about>`_ as part of `OklahomaData.org <http://www.oklahomadata.org`_.

License
=======

MIT.
