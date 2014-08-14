from __future__ import with_statement
import os

import mysql.connector

from fabric.api import env, local, task
from fabric.context_managers import local_tunnel

from util import Util


def snapshot_path():
    return os.path.join(env.project_home, 'db', 'snapshot.sql')


@task
def pull():
    Util.validate_role()
    config = env.config

    with local_tunnel(config['db_port']):
        local("mysqldump --user={username} --protocol=TCP --port={port} "
              "--host=localhost --password='{password}' {db_name} "
              "> tmp_snapshot.sql"
              .format(username=config['db_user'],
                      password=config['db_pass'],
                      port=config['db_port'],
                      db_name=config['db_name']
                      )
              )

    local('mv tmp_snapshot.sql {0}'.format(snapshot_path()))
    local('git add {0}'.format(snapshot_path()))
    local('git commit -m "Database snapshot from {host}"'
          .format(host=env['host_string']))


@task
def push():
    Util.validate_role()
    config = env.config

    with local_tunnel(config['db_port']):
        local("mysql --user={username} --port={port} --host=127.0.0.1 "
              "--password='{password}' {db_name} < {snapshot}"
              .format(
                  username=config['db_user'],
                  password=config['db_pass'],
                  port=config['db_port'],
                  db_name=config['db_name'],
                  snapshot=snapshot_path()
                  )
              )


@task
def update():
    '''
    Sets target's siteurl, blogname, and homepage
    '''
    Util.validate_role()
    config = env.config
    db_table = 'wp_options'
    entries = {
        'siteurl': config['site_url'],
        'blogname': config['site_name'],
        'home': config['site_url']

    }

    with local_tunnel(config['db_port']):
        cnx = mysql.connector.connect(user=config['db_user'],
                                        password=config['db_pass'],
                                        host='127.0.0.1',
                                        port=config['db_port'],
                                        database=config['db_name'])

        cnx.start_transaction()
        cursor = cnx.cursor()

        update_option = ("UPDATE `{db_table}` "
                        "SET `option_value`=%s "
                        "WHERE `option_name` LIKE %s".format(db_table=db_table))

        for key, value in entries.iteritems():
            cursor.execute(update_option, (value, key))

        cnx.commit()
        cnx.close()
