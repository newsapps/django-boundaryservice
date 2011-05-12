#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "django-boundaryservice",
    version = "0.1.0",
    description = "A reusable system for aggregating and providing API access to regional boundary data.",
    long_description = open('README.textile').read(),
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
