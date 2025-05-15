from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import APIConfig

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=APIConfig.RATE_LIMITS,
    storage_uri="memory://",
    strategy="fixed-window",
)