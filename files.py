from __future__ import with_statement
import os

from fabric.api import env, task
from fabric.contrib.project import rsync_project

from util import Util


def normalised_remote_path():
    remote_dir = env.config['base_path']
    if remote_dir[:1] != '/':
        return '{0}/'.format(remote_dir)

    return remote_dir


def normalised_local_wp_path():
    return os.path.join(env.project_home, 'wp/')


@task
def pull():
    Util.validate_role()
    rsync_project(remote_dir=normalised_remote_path(),
                  local_dir=normalised_local_wp_path(),
                  upload=False
                  )


@task
def push():
    Util.validate_role()
    rsync_project(remote_dir=normalised_remote_path(),
                  local_dir=normalised_local_wp_path(),
                  upload=True
                  )
