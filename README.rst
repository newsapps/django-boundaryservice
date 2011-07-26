The Newsapps Boundary Service
=============================

The Boundary Service is a ready-to-deploy system for aggregating regional boundary data (from shapefiles) and republishing that data via a RESTful JSON API.  It is packaged as a pluggable Django application so that it can be easily integrated into any project. The best example of a complete Boundary Service implementation is `hacktyler-boundaryservice <https://github.com/hacktyler/hacktyler-boundaryservice>`_.

This project is aimed at providing a simple service for newsrooms, open-government hackers and others to centralize and build on regional GIS data.  For more inspiration you can see the instance we've configured for Chicago & Illinois, along with usaer documentation for the API at `http://boundaries.tribapps.com/ <http://boundaries.tribapps.com/>`_.

Installation
============

To install django-boundaryservice use pip::

    pip install django-boundaryservice

Using the shapefile loader
==========================

By default the shapefile loader will expect you to have created the path "data/shapefiles" relative to your manage.py script. Shapefiles and your definitions.py go into this folder. See `boundaryservice demo site <https://github.com/newsapps/boundaryservice>`_ for a complete example. You may also override the default location by passing the "-d" flag to the command or setting SHAPEFILES_DIR in settings.py::

    python manage.py load_shapefiles -d data_dir

Adding data
===========

To add data to the Boundary Service you will first need to add a shapefile and its related files (prj, dbf, etc.) to the data/shapefiles directory. See data/shapefiles/neighborhoods for an example shapefile.

Once your data is in place, you will modify data/shapefiles/definitions.py to add a declaration for your new shapefile to the SHAPEFILES dictionary. The Chicago neighborhoods example includes extensive commenting describing the various fields and how they should be populated. Note that the Boundary Service will normally be able to infer the projection of your shapefile and automatically transform it to an appropriate internal representation.

Of particular note amongst the fields are the 'ider' and 'namer' properties. These should be assigned to functions which will be passed a feature's attributes as a dictionary. 'ider' should return a unique external id for the feature. (e.g. a district id number, geographic id code or any sequential primary key) Whenever possible these ids should be stable across revisions to the dataset. 'namer' should return a canonical name for the feature, not including its kind. (e.g. "Austin" for the Austin Community Area, "Chicago" for the City of Chicago, or #42 for Police Beat #42) A number of callable classes are defined in data/shapefiles/utils.py, which should mitigate the need to write custom functions for each dataset. 

Once definitions.py has been saved the new shapefile can be loaded by running::

    python manage.py load_shapefiles -o BoundaryKindWithoutWhitespace

The "-c" parameter can also be passed to clear existing boundaries of only the specified type and then load the data. Multiple boundaries can be cleared and loaded by passing a comma-separated list to "-o".

As a matter of best practice when shapefiles have been acquired from government entities and other primary sources it is advisable not to modify them before loading them into the Boundary Service. (Thus why the Chicago neighborhoods shapefile is misspelled "Neighboorhoods".) If it is necessary to modify the data this should be noted in the 'notes' field of the shapefile's definitions.py entry.

Credits
=======

The Boundary Service is a product of the `News Applications team <http://blog.apps.chicagotribune.com>`_ at the Chicago Tribune. Core development was done by `Christopher Groskopf <http://twitter.com/onyxfish>`_ and `Ryan Nagle <http://twitter.com/ryannagle>`_.

License
=======

MIT.
