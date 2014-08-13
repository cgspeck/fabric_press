import os
from fabric.api import abort, env

import misc  # noqa
import db  # noqa
import files  # noqa

try:
    import local_settings  # noqa
except ImportError, e:
    abort('You need to create a local_settings.py file and override '
          'env.roledefs and stored_config.'
          )
except Exception, e:
    raise e

env.project_home = os.path.realpath(os.path.dirname(os.path.abspath(__file__))
                                + '/..')  # noqa
