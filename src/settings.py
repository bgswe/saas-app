import os

HASH_ALGORITHM = "HS256"

APPLICATION_NAME = os.getenv("APPLICATION_NAME")

ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
ACCESS_TOKEN_DURATION = os.getenv("ACCESS_TOKEN_DURATION")

REFRESH_TOKEN_SECRET = os.getenv("REFRESH_TOKEN_SECRET")
REFRESH_TOKEN_DURATION = os.getenv("REFRESH_TOKEN_DURATION")
