import dotenv

environment_vars = dotenv.dotenv_values(".env")

def get_environment_var(name, default = ""):
    if name in environment_vars.keys():
        return environment_vars[name]

    return default

DB_PATH = get_environment_var("DB_PATH", "./mba.sqlite")