"""
    setup
    ~~~~~

    :copyright: 2016 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import os
import re
from pathlib import Path

from setuptools import setup


PROJECT_PATH = Path(__file__).parent.absolute()
PACKAGE_PATH = PROJECT_PATH / 'gf256'


def get_version():
    with (PACKAGE_PATH / '__init__.py').open(encoding='utf-8') as module:
        for line in module:
            match = re.match(r"__version__ = '([^']*)'", line)
            if match:
                return match.group(1)
    raise ValueError('__version__ not found')


def get_readme():
    # Required because Python < 3.5 doesn't have .read_text()
    with (PROJECT_PATH / 'README.rst').open(encoding='utf-8') as readme:
        return readme.read()


if os.environ.get('GF256_WITHOUT_SPEEDUPS', '1') == '1':
    keywords = {}
else:
    keywords = {
        'setup_requires': ['cffi>=1.7.0'],
        'install_requires': ['cffi>=1.7.0'],
        'cffi_modules': ['gf256/speedups_build.py:ffibuilder'],
    }

setup(
    name='GF256',
    version=get_version(),
    description="An implementation of GF(2**8)",
    long_description=get_readme(),
    url='https://github.com/DasIch/gf256/',
    author='Daniel Neuhäuser',
    author_email='ich@danielneuhaeuser.de',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    packages=['gf256'],
    **keywords
)
