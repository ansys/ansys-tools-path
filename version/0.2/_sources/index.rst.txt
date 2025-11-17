..
   Just reuse the root readme to avoid duplicating the documentation.
   Provide any documentation specific to your online documentation
   here.


.. toctree::
   :hidden:
   :maxdepth: 3

   api
   contribute


=====================================================
``ansys-tools-path``: A tool to locate Ansys products
=====================================================

How to install
==============

.. include:: ../../README.rst
   :start-after: .. howtoinstallusers_start
   :end-before: .. howtoinstallusers_end


How to use
----------

You can use any of the functions available in the :ref:`ref_api`
to identify the path of the local ANSYS installation.

For example you can use :func:`find_ansys <ansys.tools.path.find_ansys>`
to locate the path of the latest ANSYS installation available:

.. code:: pycon

   >>> from ansys.tools.path import find_ansys
   >>> find_ansys()
   'C:/Program Files/ANSYS Inc/v211/ANSYS/bin/winx64/ansys211.exe', 21.1

