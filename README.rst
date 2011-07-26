The Newsapps Boundary Service
=============================

The Boundary Service is a ready-to-deploy system for aggregating regional boundary data (from shapefiles) and republishing that data via a RESTful JSON API. It is packaged as a pluggable Django application so that it can be easily integrated into any project.

The best example of a complete Boundary Service implementation is `hacktyler-boundaryservice <https://github.com/hacktyler/hacktyler-boundaryservice>`_. For more inspiration you can see the instance we've configured for Chicago at `http://boundaries.tribapps.com/ <http://boundaries.tribapps.com/>`_.

Installation
============

Using pip::

    $ pip install django-boundaryservice

Adding data
===========

To add data you will first need to add a shapefile and its related files (prj, dbf, etc.) to the data/shapefiles directory. Shapefiles and your definitions.py go into this folder. See the `hacktyler demo site <https://github.com/hacktyler/hacktyler-boundaryservice>`_ for a complete example. 

You can load all definitions like so::

    $ python manage.py load_shapefiles

You may also override the default location by passing the "-d" flag to the command or setting SHAPEFILES_DIR in settings.py::

    $ python manage.py load_shapefiles -d data_dir

A particular shapefile like so::

    $ python manage.py load_shapefiles -o ShapeFileName

You can clear a particular shapefile from the database and reload it like so::

    $ python manage.py load_shapefiles -c ShapeFileName

Of particular note amongst the defintion fields are the 'ider' and 'namer' properties. These should be assigned to functions which will be passed a feature's attributes as a dictionary. 'ider' should return a unique external id for the feature. (e.g. a district id number, geographic id code or any sequential primary key). Whenever possible these ids should be stable across revisions to the dataset. 'namer' should return a canonical name for the feature, not including its kind. (e.g. "Austin" for the Austin Community Area, "Chicago" for the City of Chicago, or #42 for Police Beat #42) A number of callable classes are defined in data/shapefiles/utils.py, which should mitigate the need to write custom functions for each dataset. 

Advice
======

As a matter of best practice when shapefiles have been acquired from government entities and other primary sources it is advisable not to modify them before loading them into the Boundary Service. (Thus why the Chicago neighborhoods shapefile is misspelled "Neighboorhoods".) If it is necessary to modify the data this should be noted in the 'notes' field of the shapefile's definitions.py entry.

Credits
=======

The Boundary Service is a product of the `News Applications team <http://blog.apps.chicagotribune.com>`_ at the Chicago Tribune. Core development was done by `Christopher Groskopf <http://twitter.com/onyxfish>`_ and `Ryan Nagle <http://twitter.com/ryannagle>`_.

License
=======

MIT.
