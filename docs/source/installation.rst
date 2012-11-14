******************************
Installing yawd-translations
******************************

.. _install:

You can install yawd-translations either by using the python package index or 
the source code. The source code is expected to include all latest fixes and
patches.

Python package
++++++++++++++

This is the easiest, one-step installation process::

   pip install yawd-translations
    

From source
+++++++++++ 

Alternatively, you can install yawd-translations from the source code 
(visit the github page `here <https://github.com/yawd/yawd-translations>`_)::

   git clone https://github.com/yawd/yawd-translations
   cd yawd-translations
   python setup.py install

.. _prerequisites:

Prerequisites
+++++++++++++

yawd-translations needs Django v1.4 or later installed. Some of its functionality will
not work with older django versions since it uses the 
`prefetch_related <https://docs.djangoproject.com/en/dev/ref/models/querysets/#prefetch-related>`_
queryset method introduced in Django 1.4. 

It also requires that `yawd-elfinder <https://github.com/yawd/yawd-elfinder>`_
is installed (to optionally manage an accompanying language flag image). The
yawd-translations installer will install yawd-elfinder for you, 
you only need to add `elfinder` to the list of the ``INSTALLED_APPS``.

.. note::
	
	If you do not intend to use the yawd-translations language management
	mechanism (i.e. you only want to use :ref:`translations-middleware`
	with the :ref:`translation-patterns` URL resolver) 
	you do not need to include ``yawd-elfinder``, nor ``translations`` in your ``INSTALLED_APPS`` setting.
	The :ref:`usage` guide clearly describes when these applications must be enabled.