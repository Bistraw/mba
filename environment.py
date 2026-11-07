import dotenv

environment_vars = dotenv.dotenv_values(".env")

def get_environment_var(name, default = ""):
    if name in environment_vars.keys():
        return environment_vars[name]

    return default

DB_PATH = get_environment_var("DB_PATH", "./mba.sqlite")
JELLY_APIKEY = get_environment_var("JELLY_APIKEY", "")
REMOTE_APIKEY = get_environment_var("REMOTE_APIKEY", "")
REMOTE_ADDRESS = get_environment_var("REMOTE_ADDRESS", "")