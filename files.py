from __future__ import with_statement
import os
import pprint
import StringIO

from fabric.api import env, task, abort, put
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


@task
def write_config():
    '''
    Sets correct values in target's wp_config.php so that it matches the
    stored_config, principally the db_user, db_pass, db_name, wp_debug.
    e.g.:
        wp_path
        wp_url
    '''
    Util.validate_role()
    corrections = [
        {
            'startswith': "define('DB_NAME', ",
            'key': 'db_name',
            'template': "define('DB_NAME', '{value}');"
        },
        {
            'startswith': "define('DB_USER', ",
            'key': 'db_user',
            'template': "define('DB_USER', '{value}');"
        },
        {
            'startswith': "define('DB_PASSWORD', ",
            'key': 'db_pass',
            'template': "define('DB_PASSWORD', '{value}');"
        },
        {
            'startswith': "define('WP_DEBUG', ",
            'key': 'debug_mode',
            'template': "define('WP_DEBUG', '{value}');"
        }
    ]

    for correction in corrections:
        correction['pending'] = True

    original_fh = open(os.path.join(env.project_home, 'wp', 'wp-config.php'))


    in_fh = StringIO.StringIO(original_fh.read())
    out_fh = StringIO.StringIO()

    line_written = False

    for line in in_fh.readline():
        line_written = False
        for correction in corrections:
            if correction['pending']:
                if line.startswith(correction['startswith']):
                    out_fh.write(correction['template'].format(
                        value=env['config'][correction['key']]
                        )
                    )
                    line_written = True
                    correction['pending'] = False
        if not line_written:
            out_fh.write(line)

        line = in_fh.readline()

    in_fh.close()

    if any([correction['pending'] for correction in corrections]):
        print('One or more corrections not applied!')
        pprint.pprint(corrections)
        abort('')

    put(out_fh, os.path.join(env.config['base_path'],'wp-config.php'))

    out_fh.close()
