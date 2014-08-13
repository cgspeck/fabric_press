============
Fabric Press
============

Fabric based management of WordPress installations on remote shared hosts.

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

    git submodule add git@github.com:cgspeck/fabric_press.git fabric

4. Create a fabric/local_settings.py, redefining env.roledefs and 
   env.stored_config. Look at lines 9 and 14 of misc.py for an example.

5. Add and commit your local_settings.py to your submodule checkout.

6. Go up to your project directory and commit the fabric_press submodule.

7. Start using fabric to manage your WordPress instance.

Keeping Up to date
==================

Standard git instructions for updating a submodule, i.e.::

    cd fabric
    git checkout master
    git pull
    cd ..
    git add fabric
    git commit -m "Updated fabric_press"
    git push


Usage Examples
==============

This requires ssh keys to be set up for the user account under which you intend
to run it, so that the local user is able to ssh to the remote machine.

Grab files and database from dev::

    fab -R dev files.pull
    fab -R dev database.pull

Then you would use git to review and changes commit any properly changed or
additional file.

Likewise, grabbing files from production::

    fab -R prod files.pull
    fab -R prod database.pull

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
    fab -R prod database.push


License & Copyright
===================
Copyright (c) 2014, Christopher Speck
http://www.chrisspeck.com
https://github.com/cgspeck

This application is subject to the revised 3-clause BSD license, as set out in
the LICENSE  file found in the top-level directory of this distribution. USE AT
YOUR OWN RISK AND ONLY AFTER TAKING A BACKUP.