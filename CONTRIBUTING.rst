Contributing
============


Setting up a Development Environment
------------------------------------

1. Clone the repository.
2. Create a virtual environment.
3. Install development dependencies::

     pip install -r dev-requirements


Running Tests
-------------

Run tox to make sure everything works correctly on your machine::

  tox


Building the Documentation
--------------------------

You can build the documentation with::

  make -C docs html

If the command succeeds, you can view the documentation by opening
`docs/_build/html/index.html` in a browser.
