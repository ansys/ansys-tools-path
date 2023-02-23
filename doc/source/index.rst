..
   Just reuse the root readme to avoid duplicating the documentation.
   Provide any documentation specific to your online documentation
   here.


.. toctree::
   :hidden:
   :maxdepth: 3

   API


.. include:: ../../README.rst
   :end-before: .. howtouse



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


.. include:: ../../README.rst
   :start-after: .. howtouse