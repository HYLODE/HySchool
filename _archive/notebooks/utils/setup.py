import os
from dotenv import load_dotenv
from pathlib import Path


def load_env_vars(
    ENV_FILE_ID = 'moons.gentle.making',
    dotenv_path = './config/.env'
                 ):
    """
    Load environment variables or raise error if the file is not found
    """
    dotenv_path = Path(dotenv_path)
    load_dotenv(dotenv_path=dotenv_path)

    if os.getenv('ENV_FILE_ID') != ENV_FILE_ID:
        raise FileNotFoundError("""
        IMPORTANT
        An environment file holding the ENV_FILE_ID variable equal to 'moons.gentle.making'
        should have been found at the ./config/.env path.

        Is the script being run from the repository root (emap-helper/)?
        Did you convert the example 'env' file to the '.env' file?

        Please check the above and try again 
        """)
    else:
        return True
    
    
def make_emap_engine():
    # Load environment variables
    load_env_vars()

    # Construct the PostgreSQL connection
    uds_host = os.getenv('EMAP_DB_HOST')
    uds_name = os.getenv('EMAP_DB_NAME')
    uds_port = os.getenv('EMAP_DB_PORT')
    uds_user = os.getenv('EMAP_DB_USER')
    uds_passwd = os.getenv('EMAP_DB_PASSWORD')

    emapdb_engine = create_engine(f'postgresql://{uds_user}:{uds_passwd}@{uds_host}:{uds_port}/{uds_name}')
    return emapdb_engine

