============
Fabric Press
============

Fabric based management of `WordPress <https://wordpress.org/download/>`_
installations on remote shared hosts.

This allows a WordPress sysadmin to create a dev version of their site, give
full access to a designer, and then syncronise the files and database to a
local git server and then push it out to your production server.

You can also grab the production files and production database, and push it
to your dev server to keep that in sync with changes on production.

An added bonus of this is that you will be able to use git for free backup
and versioning of changes to your site.

I'd like to implement the following in the future (but no guarantees):

* disable nominated accounts on production;
* use uwsgi and a local mysql to serve a copy of site;
* handle wordpress tables with a prefix other than ``wp_``

Pull requests are welcome.

Installation
============

This is designed to be run within a Python 2.7 virtual environment. As at the
time of writing, Fabric was not officially up to Python 3x.

1. Create a folder on your local machine to host your WordPress project and
   initialise a git repo.

2. Install Fabric from `here <https://github.com/cgspeck/fabric>`_. After pull
   request `939 <https://github.com/fabric/fabric/pull/939>`_ is merged you
   will be able to install Fabric direct from upstream.

3. Add this repo as a subtree to your project::

    git remote add -f fabric_press git@github.com:cgspeck/fabric_press.git
    git subtree add --prefix fabfile fabric_press master --squash

4. Install the mysql-python-connector::

    pip install mysql-connector-python --allow-external mysql-connector-python

5. Create a ``fabfile/localsettings.py``, import ``fabric.api.env`` and
   redefine ``env.roledefs`` and ``env.stored_config``::

    from fabric.api import env

    env.roledefs = ...
    env.stored_config = ...

   Look at lines 9 and 14 of ``misc.py`` for an example.

6. Add and commit your ``localsettings.py``.

7. Start using fabric to manage your WordPress instance.


Keeping Up to date
==================

Standard git instructions for updating a subtree, i.e.::

 git fetch fabric_press master
 git subtree pull --prefix fabfile fabric_press master --squash


Usage Examples
==============

This requires ssh keys to be set up for the user account under which you intend
to run it, so that the local user is able to ssh to the remote machine.

Backup/grab files and database from dev::

    fab -R dev files.pull
    fab -R dev db.pull

Then you would use git to review and changes commit any properly changed or
additional file.

Likewise, grabbing files and database from production::

    fab -R prod files.pull
    fab -R prod db.pull

**WARNING: This is simply an automation tool - do not attempt to push files or
a database to a target unless you are intimately familiar with the process of
manually moving WordPress from one server to another. This may require you to
use other tools and knowledge (e.g. digging around MySQL) to restore 
functionality of the site. Automatically fixing the database and wp-config.php
is not guaranteed and the author is unable to assist in any way should your
site be rendered unusable following a push command.**

Example pushing files to production::

    fab -R prod files.push
    fab -R prod db.push

Then updating production database and config::

    fab -R prod files.write_config
    fab -R prod db.update

**NOTE: It is unable to update WordPress database if the tables do not start
with the default prefix of ``wp_``, specifically, options table must be
``wp_options`` within the database.**

Using it to transfer a WP Instance
----------------------------------

On your new/existing host of choice, create:

1. a domain/subdomain;
2. a new mysql database

For the sake of this example, the old host will be ``dev`` and new will be
``staging``. In your ``localsettings.py``, define two roles, new and old e.g::

    from fabric.api import env


    env.roledefs = {
        'dev': ['user@example.local'],
        'staging': ['user@example.com']
    }

    env.stored_config = {
        'dev': {
            'base_path': '/var/www/public_html/',
            'db_port': 3306,
            'db_user': 'user',
            'db_pass': 'pass',
            'db_name': 'wordpress',
            'site_name': 'Development Site',
            'site_path': 'example.local',
            'set_maintenance_mode': False,
            'debug_mode': True
        },
        'staging': {
            'base_path': '/home/user/public_html/',
            'db_port': 3306,
            'db_user': 'user',
            'db_pass': 'pass',
            'db_name': 'name',
            'site_name': 'Staging site',
            'site_path': 'staging.example.com',
            'set_maintenance_mode': True,
            'debug_mode': True
        }
    }

Then pull the database & files, and then push back to new host::

    fab -R dev files.pull
    fab -R dev database.pull
    fab -R dev database.push
    fab -R staging files.push

Then rewrite ``wp-config.php`` on staging::

    fab -R staging files.write_config

And update database on staging::

    fab -R staging database.update


Removing Submodules
-------------------

Previous version of this readme suggested using a submodule to refer to Fabric
Press, but this is not the correct approach as the contents of the submodule
was not actually pushed to the parent repo.

To remedy this:

1. Copy your localsettings.py somewhere safe out of the /fabfile directory.

2. Run the following to purge your repo of submodule::

     git submodule deinit fabfile
     git rm -rf fabfile

3. Follow instruction no 3 within the installation section.

4. Copy your localsettings.py file back in place, stage, commit, push.


License & Copyright
===================
Copyright (c) 2014, `Christopher Speck <http://www.chrisspeck.com>`_.

Repo hosted on `Github <https://github.com/cgspeck>`_.

This application is subject to the revised 3-clause BSD license, as set out in
the LICENSE  file found in the top-level directory of this distribution. USE AT
YOUR OWN RISK AND ONLY AFTER TAKING A BACKUP.
