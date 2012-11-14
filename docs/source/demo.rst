.. _demo-project:

************
Demo project
************

Use the provided demo project for a quick example of yawd-translations. 
You can install it on an isolated environment using virtualenv. Firstly, 
install virtualenv::

   $ apt-get-install virtualenv
   
Create a new environment named *yawdtranslations* and activate it::

   $ virtualenv /www/yawdtranslations
   $ source /www/yawdtranslations/bin/activate
   
Download and install yawd-translations::

   $ git clone https://github.com/yawd/yawd-translations
   $ cd yawd-translations
   $ python setup.py install
   
At this point, yawd-translations will be in your ``PYTHONPATH``. Now initialize 
the example project::
   
   $ cd example_project
   $ python manage.py syncdb
   
When promted, create an admin account. Finally, start the web server::

   $ python manage.py runserver
   
...and visit *http://localhost:8000/admin/*
to see the admin interface and experiment with the languages, the translation
messages and the translatable model. A quick demo site is accessible at 
*http://localhost:8000/*.

Once you are done, you can deactivate the virtual environment::

   $ deactivate yawdtranslations