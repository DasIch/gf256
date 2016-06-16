"""
    setup
    ~~~~~

    :copyright: 2016 by Daniel Neuhäuser
    :license: BSD, see LICENSE.rst for details
"""
from pathlib import Path

from setuptools import setup


PROJECT_PATH = Path(__file__).parent.absolute()


setup(
    name='GF256',
    version='0.1',
    description="An implementation of GF(2**8)",
    long_description=(PROJECT_PATH / 'README.rst').read_text(),
    url='https://github.com/DasIch/gf256/',
    author='Daniel Neuhäuser',
    author_email='ich@danielneuhaeuser.de',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython'
    ]
)
