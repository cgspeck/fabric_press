from __future__ import with_statement
import pprint
import tempfile
import StringIO

from fabric.api import env, abort, local, put, task
from fabric.contrib.project import rsync_project


env.roledefs = {
    'dev': ['devuser@host:22'],
    'prod': ['produser@host:22']
}

env.stored_config = {
    'dev': {
        'base_path': '/path/to/dev/wordpress/',  # noqa: be sure to add the trailing slash!!
        'db_port': 3306,
        'db_user': 'dev_db_username',
        'db_pass': 'dev_db_password',
        'db_name': 'dev_db_name',
        'site_name': 'Site Name Dev',
        'site_path': 'dev.example.com',
        'set_maintenance_mode': True,
        'debug_mode': True
    },
    'prod': {
        'base_path': '/path/to/prod/wordpress/',  # noqa: be sure to add the trailing slash!!
        'db_port': 3306,
        'db_user': 'prod_db_username',
        'db_pass': 'prod_db_password',
        'db_name': 'prod_db_name',
        'site_name': 'Site Name',
        'site_path': 'www.example.com',
        'set_maintenance_mode': False,
        'debug_mode': False
    }
}


@task
def ipdb():
    from pprint import pprint  # noqa
    from ipdb import set_trace
    set_trace()
