Contributing
============


Setting up a Development Environment
------------------------------------

1. Clone the repository_::

     git clone https://github.com/DasIch/gf256.git

2. Create a virtual environment.
3. Install development dependencies::

     pip install -r dev-requirements.txt


.. _repository: https://github.com/DasIch/gf256


Running Tests
-------------

We use a variety of tools to test the projects. You can run all of them locally
with tox_::

  tox

You should run this at least once before committing but it takes an
inconvenient amount of time especially for TDD. Use pytest_ to only run the
unit tests::

  py.test

We also use two CI platforms `Travis CI`_ and `AppVeyor`_ to test everything on
Linux and Windows respectively.

.. _tox: http://tox.readthedocs.io/
.. _pytest: http://pytest.org/
.. _Travis CI: https://travis-ci.org/DasIch/gf256
.. _AppVeyor: https://ci.appveyor.com/project/DasIch/gf256


Building the Documentation
--------------------------

You can build the documentation with::

  make -C docs html

If the command succeeds, you can view the documentation by opening
`docs/_build/html/index.html` in a browser.
