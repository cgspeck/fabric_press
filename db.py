from __future__ import with_statement
import os

import mysql.connector

from fabric.api import env, local, task, abort
from fabric.context_managers import local_tunnel
from fabric.utils import puts

from util import Util


def snapshot_path(suffix):
    if suffix:
        return os.path.join(env.project_home, 'db', 'snapshot-{0}.sql'.format(suffix))
    else:
        os.path.join(env.project_home, 'db', 'snapshot.sql')

@task
def pull():
    '''
    Backup remote database to sql file.
    '''
    Util.validate_role()
    config = env.config

    _run_mysql_dump(config)
    _move_snapshot(snapshot_path('remote'))


@task
def backup_local():
    '''
    Backup local database to sql file. If you want to push it, then you need to manually rename it.
    '''
    if env['roles'] != ['local']:
        abort('This should only be run against a local development database')

    Util.validate_role()
    config = env.config

    _run_mysql_dump(config)
    _move_snapshot(snapshot_path('local'))


def _move_snapshot(dest):
    '''
    Called by higher level tasks to organise mysql dumps
    '''
    local('mv tmp_snapshot.sql {0}'.format(dest))
    local('git add {0}'.format(dest))
    local('git commit -m "Database snapshot from {host}"'
          .format(host=env['host_string']))


def _run_mysql_dump(config):
    '''
    Runs the mysqldump against local or remote database
    '''

    def mysql_command():
        local("mysqldump --user={username} --protocol=TCP --port={port} "
              "--host=localhost --password='{password}' {db_name} "
              "> tmp_snapshot.sql"
              .format(username=config['db_user'],
                      password=config['db_pass'],
                      port=config['db_port'],
                      db_name=config['db_name']
            )
        )

    if env['roles'] == ['local']:
        mysql_command()
    else:
        with local_tunnel(config['db_port']):
            mysql_command()    


@task
def push():
    '''
    Push copy of remote database to local or remote server.
    '''    
    Util.validate_role()
    config = env.config

    def mysql_command():
        local("mysql --user={username} --port={port} --host=127.0.0.1 "
              "--password='{password}' {db_name} < {snapshot}"
              .format(
            username=config['db_user'],
            password=config['db_pass'],
            port=config['db_port'],
            db_name=config['db_name'],
            snapshot=snapshot_path('remote')
            )
        )

    if env['roles'] == ['local']:
        mysql_command()
    else:
        with local_tunnel(config['db_port']):
            mysql_command()


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

    def mysql_command():
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

    if env['roles'] == ['local']:
        mysql_command()
    else:
        with local_tunnel(config['db_port']):
            mysql_command()


def nuke():
    '''
    Clears out local development database
    '''
    if env['roles'] != ['local']:
        abort('This should only be run against a local development database')

    Util.validate_role()
    config = env.config
    cnx = mysql.connector.connect(user=config['db_user'],
                                  password=config['db_pass'],
                                  host='127.0.0.1',
                                  port=config['db_port'],
                                  database=config['db_name'])

    cnx.start_transaction()
    cursor = cnx.cursor()
    cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')

    find_tables_query = ("SELECT concat('DROP TABLE IF EXISTS ', table_name, ';') "
                        "FROM information_schema.tables "
                        "WHERE table_schema = '%s';" % (config['db_name']))
    puts(find_tables_query)
    cursor.execute(find_tables_query)
    drop_tables_queries = cursor.fetchall()

    for statement in drop_tables_queries:
        puts(statement[0])
        cursor.execute(statement[0])

    cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')
    cnx.commit()
    cnx.close()
