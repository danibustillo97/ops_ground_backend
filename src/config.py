import os
from decouple import config

SECRET_KEY = config("SECRET_KEY", default="arajet_2024")
ALGORITHM = config("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=30)
