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
* flip maintenance and debug modes on and off;
* fix settings in wp-config.ini appropriate for target environment;
* use uwsgi and a local mysql to serve a copy of site;

Pull requests are welcome.

Installation
============

1. Create a folder on your local machine to host your WordPress project and
   initialise a git repo.

2. Install Fabric from `here <https://github.com/cgspeck/fabric>`_. After pull
   request `939 <https://github.com/fabric/fabric/pull/939>`_ is merged you
   will be able to install Fabric direct from upstream.

3. Add this repo as a submodule to your project::

    git submodule add git@github.com:cgspeck/fabric_press.git fabfile

4. Create a ``fabfile/local_settings.py``, importing ``fabric.api.env`` and
   redefining ``env.roledefs`` and ``env.stored_config``::

    from fabric.api import env

    env.roledefs = ...
    env.stored_config = ...

   Look at lines 9 and 14 of ``misc.py`` for an example.

5. Add and commit your ``local_settings.py`` to your submodule checkout::

    git add local_settings.py
    git commit -m "Added local settings for my site"

6. Go up to your project directory and commit the ``fabric_press`` submodule::

    cd ..
    git add fabfile
    git commit -am "Added Fabric Press submodule :-)"


7. Start using fabric to manage your WordPress instance.

Keeping Up to date
==================

Standard git instructions for updating a submodule, i.e.::

    cd fabfile
    git checkout master
    git pull
    cd ..
    git commit -am "Updated fabric_press"
    git push


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
functionality of the site. Automatically fixing the database and wp-config.ini 
after a push is not implemented and the author is unable to assist in any way
should your site be rendered unusable following a push command.**

*Note*: after pushing files you will have to check and update wp-config.ini
so that it has the proper database settings for your target.

*Note*: after pushing a database you will have to check and update various
fields within it so that WordPress will function correctly on the target.

Example pushing files to production::

    fab -R prod files.push
    fab -R prod db.push


Using it to transfer a WP Instance
----------------------------------

On your new/existing host of choice, create:

1. a domain/subdomain;
2. a new mysql database

For the sake of this example, the old host will be ``dev`` and new will be
``staging``. In your ``local_settings.py``, define two roles, new and old e.g::

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

    fab -R staging misc.write_config

And update database on staging::

    fab -R staging database.update

License & Copyright
===================
Copyright (c) 2014, Christopher Speck
http://www.chrisspeck.com
https://github.com/cgspeck

This application is subject to the revised 3-clause BSD license, as set out in
the LICENSE  file found in the top-level directory of this distribution. USE AT
YOUR OWN RISK AND ONLY AFTER TAKING A BACKUP.