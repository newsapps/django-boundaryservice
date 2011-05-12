#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "django-boundaryservice",
    version = "0.1.3",
    description = "A reusable system for aggregating and providing API access to regional boundary data.",
    long_description = 'See `django-boundaryservice <https://github.com/newsapps/django-boundaryservice>`_ on Github for more information.',
    author='Christopher Groskopf',
    author_email='staringmonkey@gmail.com',
    url='http://blog.apps.chicagotribune.com/',
    license = "MIT",
    packages = [
        'boundaryservice',
        'boundaryservice.management',
        'boundaryservice.management.commands'
    ],
    install_requires = [
        'django-tastypie'
    ]
)
