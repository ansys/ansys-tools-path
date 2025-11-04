..
   Just reuse the root readme to avoid duplicating the documentation.
   Provide any documentation specific to your online documentation
   here.


.. toctree::
   :hidden:
   :maxdepth: 3

   api/index
   contribute
   changelog


=====================================================
``ansys-tools-path``: A tool to locate Ansys products
=====================================================
.. warning::

   This library is deprecated and will no longer be maintained. Please consider using alternatives.
   For more information, check the `deprecation issue <https://github.com/ansys/pyansys-tools-report/issues/339>`_.

How to install
==============

.. include:: ../../README.rst
   :start-after: .. howtoinstallusers_start
   :end-before: .. howtoinstallusers_end


How to use
----------

You can use any of the functions available in the
to identify the path of the local Ansys installation.

For example you can use :func:`find_ansys <ansys.tools.path.find_ansys>`
to locate the path of the latest Ansys installation available:

.. code:: pycon

   >>> from ansys.tools.path import find_ansys
   >>> find_ansys()
   'C:/Program Files/ANSYS Inc/v251/ANSYS/bin/winx64/ansys251.exe', 25.1

