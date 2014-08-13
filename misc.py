from __future__ import with_statement
import tempfile
import pprint

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


def set_site_values():
    validate_role()
    # TODO: set_db_values()
    # TODO: set_write_wpconfig()


def update_db_values():
    '''
    Sets values stored in target's database so they match stored config,
    e.g.:
        wp_path
        wp_url
    '''
    pass


def update_wpconfig_values():
    '''
    Sets correct values in target's wp_config.ini so that it matches the
    stored_config, principally the db_user and db_pass.
    e.g.:
        wp_path
        wp_url
    '''
    validate_role()
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

    in_fd, in_fn = tempfile.mkstemp()
    local('cp wp/wp-config.php {dest}'.format(dest=in_fn))

    out_fd, out_fn = tempfile.mkstemp(text=True)

    line_written = False

    in_fh = open(in_fn)
    out_fh = open(out_fn, 'wt')

    line = in_fh.readline()
    while line:
        print(line)
        line_written = False
        for correction in corrections:
            if correction['pending']:
                if line.startswith(correction['startswith']):
                    print('ping')
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
    out_fh.close()
    print('{0} written'.format(out_fn))

    if any([correction['pending'] for correction in corrections]):
        print('One or more corrections not applied!')
        pprint.pprint(corrections)
        abort('')
    # TODO: use os.path.join
    put(out_fn, '{0}wp-config.php')

    local('rm {0}'.format(out_fn))
    local('rm {0}'.format(in_fn))
