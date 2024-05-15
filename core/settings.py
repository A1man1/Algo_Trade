from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings
from starlette.config import Config

config = Config(".env")


class Settings(BaseSettings):
    """System Settings file for app configuration.

    Args:
        BaseSettings (object): Global base settings for configuration.
    """

    # project declaratives.
    project_name: str = config("PROJECT_NAME", cast=str, default="Inventory System")
    version: str = config("VERSION", cast=str, default="1.0.0")
   
    # app settings.
    allowed_hosts: str = config("ALLOWED_HOSTS", cast=str, default="")
    environment: str = config("ENVIRONMENT", cast=str, default="TEST")
    debug: bool = False
    testing: bool = False

    #project variables 
    MEAN_REVISION:str = 'mean_revision'
    VWAP:str = 'vwap'
    

class ProdSettings(Settings):
    debug: bool = False


class DevSettings(Settings):
    debug: bool = True


class TestSettings(Settings):
    debug: bool = True
    testing: bool = True
    db_force_roll_back: bool = True
    # Define API parameters
    api_url:str = "https://www.alphavantage.co/query"   
    apikey:str ="SJEBOCCNEMXM19O1"
    symbol:str = "AAPL"
    interval:str = "1min"


class FactoryConfig:
    """
    Returns a config instance depends on the ENV_STATE variable.
    """

    def __init__(self, environment: Optional[str] = "TEST"):
        self.environment = environment

    def __call__(self):
        if self.environment == "PROD":
            return ProdSettings()
        elif self.environment == "TEST":
            return TestSettings()
        return DevSettings()


@lru_cache()
def get_app_settings():
    return FactoryConfig(Settings().environment)()