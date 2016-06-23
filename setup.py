"""
    setup
    ~~~~~

    :copyright: 2016 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
import re
from pathlib import Path

from setuptools import setup


PROJECT_PATH = Path(__file__).parent.absolute()


def get_version():
    with (PROJECT_PATH / 'gf256.py').open(encoding='utf-8') as module:
        for line in module:
            match = re.match(r"__version__ = '([^']*)'", line)
            if match:
                return match.group(1)
    raise ValueError('__version__ not found')


setup(
    name='GF256',
    version=get_version(),
    description="An implementation of GF(2**8)",
    long_description=(PROJECT_PATH / 'README.rst').read_text(),
    url='https://github.com/DasIch/gf256/',
    author='Daniel Neuhäuser',
    author_email='ich@danielneuhaeuser.de',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    py_modules=['gf256']
)
