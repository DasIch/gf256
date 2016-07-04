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


Usage
-----

The library provides a class :class:`~gf256.GF256` which you can use to
represent elements of `GF(2 ** 8)`.

>>> from gf256 import GF256
>>> GF256(1)
GF256(0b00000001)

You can perform arithmetic on `GF256` objects like you can on other numbers.

>>> GF256(1) + GF256(2)
GF256(0b00000011)
>>> GF256(1) - GF256(2)
GF256(0b00000011)
>>> GF256(2) * GF256(3)
GF256(0b00000110)
>>> GF256(6) / GF256(3)
GF256(0b00000010)

In addition to the special methods required for arithmetic, `GF256` provides
special methods for coercion to integers and hashing:

>>> int(GF256(1))
1
>>> hash(GF256(2))
2

The latter allows you to use `GF256` objects as keys in dictionaries or as
elements of a set. Of course equality and inequality comparisons are also
possible.


API Reference
-------------

.. module:: gf256

.. autodata:: gf256.__version__
   :annotation: = 'major.minor.bugfix'

.. autodata:: gf256.__version_info__
   :annotation: = (major, minor, bugfix)

.. autoclass:: gf256.GF256
   :inherited-members:
   :members:

.. autoclass:: gf256.GF256LT
   :inherited-members:
   :members:


Additional Information
----------------------

.. toctree::
   :maxdepth: 2

   changelog
   contributing
   license
