from __future__ import with_statement

from fabric.api import env, abort, task
from fabric.utils import puts

from . import files, db
from subprocess import Popen, PIPE
from util import Util


env.roledefs = {    # you can have whatever roles you like as long as it is defined like this
    'dev': ['devuser@host:22'],
    'staging': ['devuser@host:22'],
    'prod': ['produser@host:22']
}

env.fab_server_port = 8080

env.stored_config = {
    'dev': {
        'base_path': '/path/to/dev/wordpress/',  # noqa: be sure to add the trailing slash!!
        'db_port': 3306,
        'db_user': 'dev_db_username',
        'db_pass': 'dev_db_password',
        'db_name': 'dev_db_name',
        'site_name': 'Site Name Dev',
        'site_url': 'http://dev.example.com',
        'debug_mode': False  # according to WordPress this only helps theme and plugin developers
    },
    'staging': {
        'base_path': '/path/to/dev/wordpress/',  # noqa: be sure to add the trailing slash!!
        'db_port': 3306,
        'db_user': 'stg_db_username',
        'db_pass': 'stg_db_password',
        'db_name': 'stg_db_name',
        'site_name': 'Site Name Staging',
        'site_url': 'http://staging.example.com',
        'debug_mode': False
    },
    'prod': {
        'base_path': '/path/to/prod/wordpress/',  # noqa: be sure to add the trailing slash!!
        'db_port': 3306,
        'db_user': 'prod_db_username',
        'db_pass': 'prod_db_password',
        'db_name': 'prod_db_name',
        'site_name': 'Site Name',
        'site_url': 'http://www.example.com',
        'debug_mode': False
    },
    'local': {
        'base_path': '/path/to/prod/wordpress/',  # noqa: be sure to add the trailing slash!!
        'db_port': 3306,
        'db_user': 'wp_dev',
        'db_pass': 'wp_dev',
        'db_name': 'wp_dev',
        'site_name': 'Site Name',
        'site_url': 'http://localhost:{0}'.format(env.fab_serve_task_port),
        'debug_mode': True
    }
}


@task
def ipdb():
    '''
    Open up the ipdb console (dev and debugging only!)
    '''
    from pprint import pprint  # noqa
    from ipdb import set_trace
    set_trace()


@task
def serve():
    '''
    Serve the site from command line
    '''
    if 'local' not in env.stored_config:
        abort('No local config')

    env['roles'] = ['local']
    puts("Writing new wp-config.php")
    files.write_config()
    puts("Pushing database dump to mysql")
    db.push()
    puts("Updating the database")
    db.update()
    puts("Starting PHP")
    process = Popen(['php',
                     '-S',
                     'localhost:{0}'.format(env.fab_server_port),
                     '-t',
                     '{0}'.format(Util.normalised_local_wp_path())],
                    'w',
                    shell=True,
                    stdin=PIPE
    )
    process.wait()
