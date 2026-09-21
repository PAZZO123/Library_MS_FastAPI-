from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL:str
    JWT_SECRET:str
    JWT_ALGORITHM:str
    REDIS_URL:str="redis://localhost:6379/0"
    
    MAIL_USERNAME:str
    MAIL_PASSWORD:str
    MAIL_FROM:str
    MAIL_PORT:int
    MAIL_SERVER:str
    MAIL_FROM_NAME:str
    MAIL_STARTTLS:bool=True
    MAIL_SSL_TLS:bool=False
    USE_CREDENTIALS:bool=True
    VALIDATE_CERTS:bool=True
    DOMAIN:str
    
    model_config =SettingsConfigDict(
        env_file="src/.env",
        extra="ignore"
    )
    

config= Settings()
broker_url= config.REDIS_URL
result_backend=config.REDIS_URL