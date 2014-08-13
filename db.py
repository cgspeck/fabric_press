from __future__ import with_statement
import os

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
