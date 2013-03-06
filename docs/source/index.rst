.. yawd-translations documentation master file, created by
   sphinx-quickstart on Mon Nov 12 13:46:54 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

yawd-translations django application documentation
==================================================

`yawd-translations <http://yawd.eu/open-source-projects/yawd-translations/>`_
provides a set of tools for creating multilingual websites with
`django <http://www.djangoproject.com>`_.

The application includes the following tools:

* Manage the website's installed Languages through the admin interface
* Generate translation messages (``makemessages`` and ``compilemessages``) for all installed applications and defined languages using the admin interface (no need to restart the web server).
* Translatable db models API
* A custom `admin inline <https://docs.djangoproject.com/en/dev/ref/contrib/admin/#django.contrib.admin.InlineModelAdmin>`_  to manage db translations
* A custom middleware to replace `django.middleware.locale.LocaleMiddleware <https://docs.djangoproject.com/en/dev/topics/i18n/translation/#how-django-discovers-language-preference>`_ and achieve the following:

	* Change the way django detects language preference and use the db default language (set through the admin interface)
	* Redirects to language-dependant URLs are permanent (301) and not temporary (302).
	
* A patterns function (that behaves pretty-much like django's own `i18n_patterns() <https://docs.djangoproject.com/en/dev/topics/i18n/translation/#language-prefix-in-url-patterns>`_ does) to achieve the following:

	* Match root URL paths as default language URLs: If your default language is English (``en``), ``i18n_patterns()`` will not match the ``/`` URL as the english homepage and the django middleware would redirect pages to their ``/en/`` equivalent (e.g. your homepage would be `http://example.com/en/` and all requests to `http://example.com/` would be redirected to `http://example.com/en/`). The custom patterns function implements the exact opposite, which is a common practice to web development. Therefore `http://example.com/` will be matched as the real permalink (instead of `http://example.com/en/`). For non-default languages, the custom patterns function behaves like ``i18n_patters()`` does.
	
	.. note::
		``i18n_patterns()`` can still be used with yawd-translations, so you can
		choose how you want your website permalink URLs to be

* A `context processor` to access available languages in your templates and a simple `template tag` to easily switch between the available translations of a page in the front-end website.

Django version compatibility
++++++++++++++++++++++++++++

The following yawd-translations versions might also work with other Django 
releases (older or newer), however such combinations are NOT tested.

| **yawd-translations v0.5.0:** `Django v.1.4.1 <https://www.djangoproject.com/m/releases/1.4/Django-1.4.1.tar.gz>`_
| **yawd-translations v0.5.2:** `Django v.1.4.5 <https://www.djangoproject.com/m/releases/1.4/Django-1.4.5.tar.gz>`_
| **yawd-translations v0.6.0:** `Django v.1.5.0 <https://www.djangoproject.com/download/1.5/tarball/>`_

Contents:

.. toctree::
   :maxdepth: 2
   
   installation
   usage
   demo
   ref/index

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

