from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup

setup(
    name = "represent-boundaries",
    version = "0.1",
    url='http://github.com/rhymeswithcycle/represent-boundaries',
    license = "MIT",
    packages = [
        'boundaries',
        'boundaries.management',
        'boundaries.management.commands'
    ],
    install_requires = [
        'django-tastypie==0.9.9',
        'django-jsonfield>=0.7.1',
    ]
)
