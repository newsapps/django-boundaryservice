# Represent API: Boundaries

[Represent](http://represent.opennorth.ca) is the open database of Canadian elected representatives and electoral districts. It provides a RESTful API to boundary, representative, and postcode resources.

This repository provides an API to geographic boundaries. It is based on the Chicago Tribune's [django-boundaryservice](http://github.com/newsapps/django-boundaryservice).

The [represent-canada](http://github.com/opennorth/represent-canada) repository provides a full sample app.

API documentation is available at [represent.opennorth.ca/api/](http://represent.opennorth.ca/api/#boundaryset).

## Installation

Install the package:

    python setup.py install

Add `boundaries` to INSTALLED_APPS in your settings.py.

Add the following to your urls.py:

    (r'', include('boundaries.urls')),

Run `python manage.py syncdb` (or `migrate` if you use South).

## Adding data

By default, shapefiles are expected to be in subdirectories of [project_dir]/data/shapefiles, though this can be configured via the `BOUNDARIES_SHAPEFILES_DIR` setting.

To load data, run

    python manage.py loadshapefiles

This command loads every file for which it can find a definition. It looks for definitions in files ending with `definition.py` or `definitions.py` in `BOUNDARIES_SHAPEFILE_DIR` or its subdirectories.

See the sample definition in [definition.example.py](http://github.com/rhymeswithcycle/represent-boundaries/blob/master/definition.example.py).

## Contact

Please use [GitHub Issues](http://github.com/rhymeswithcycle/represent-boundaries/issues) for bug reports. You can also contact represent@opennorth.ca.