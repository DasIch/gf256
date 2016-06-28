Welcome to GF256
================

GF256 is an implementation of `GF(2 ** 8)`. A finite field commonly used in
cryptographic algorithms.


Installation
------------

You can install the library using pip_::

  pip install gf256

The library comes with a C extension (via CFFI_) for better performance. You
can set an environment variable `GF256_WITHOUT_SPEEDUPS=1` to prevent it from
being built.

.. _pip: https://pip.pypa.io/
.. _CFFI: https://cffi.readthedocs.io/


API Reference
-------------

.. module:: gf256

.. autodata:: gf256.__version__
   :annotation: = 'major.minor.bugfix'

.. autodata:: gf256.__version_info__
   :annotation: = (major, minor, bugfix)

.. autoclass:: gf256.GF256
   :members:


Additional Information
----------------------

.. toctree::
   :maxdepth: 2

   contributing
   license
