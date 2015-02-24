from subprocess import Popen, PIPE
from util import Util
import os

from fabric.api import abort, env, task
from fabric.utils import puts


import misc  # noqa
import db  # noqa
import files  # noqa

try:
    import localsettings  # noqa
except ImportError, e:
    abort('You need to create a local_settings.py file and override '
          'env.roledefs and stored_config.'
          )
except Exception, e:
    raise e

env.project_home = os.path.realpath(os.path.dirname(os.path.abspath(__file__))
                                + '/..')  # noqa


@task
def serve():
    '''
    Serve the site from this machine
    '''
    if 'local' not in env.stored_config:
        abort('No local config')

    env['roles'] = ['local']
    puts("Writing new wp-config.php")
    files.write_config()
    puts('Backing up local database to db/snapshot-local.sql')
    db.backup_local()
    puts("Clearing local database")
    db.nuke()
    puts("Pushing copy of remote database dump to mysql")
    db.push()
    puts("Updating the database")
    db.update()
    puts("Starting PHP")

    command = "php -S localhost:{port} -t {path}".format(
        port=env.fab_server_port,
        path=Util.normalised_local_wp_path()
    )
    process = Popen(command.split())
    process.wait()
