from fabric.api import env, abort


class Util():
    @staticmethod
    def validate_role():
        if not env.roles or len(env.roles) > 1:
            abort('You must specify one and only one role')

        if not env.roles[0] in env.stored_config:
            abort('Role {0} does not have required stored_config'
                  .format(env.roles[0])
                  )
        env.config = env.stored_config[env['roles'][0]]
