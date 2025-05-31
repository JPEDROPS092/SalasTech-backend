from datetime import datetime
from datetime import timezone
import os
import logging
import jwt
from app.core.config import CONFIG

# Use environment variable or config for secret key
SECRET_KEY = os.getenv("JWT_SECRET_KEY", CONFIG.HASH_SALT)
ALGORITHM = "HS256"

# Set up logging
logger = logging.getLogger(__name__)

def encode(data: dict, exp: datetime) -> str:
    """Encode data into a JWT token with expiration time"""
    iat = datetime.now(timezone.utc).replace(tzinfo=None)
            
    token_data = {
        "iat": iat,
        "exp": exp,
        "body": data
    }
    
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

def decode(token: str) -> dict | None:
    """Decode and validate JWT token
    
    Returns:
        dict: The decoded token body if valid
        None: If token is invalid or expired
    """
    try:
        # Verify expiration during decoding
        data: dict = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM],
            options={"verify_signature": True, "verify_exp": True}
        )
        return data.get("body")
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {str(e)}")
        return None
