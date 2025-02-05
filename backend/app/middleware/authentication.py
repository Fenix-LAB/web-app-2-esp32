import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
from typing import List, Tuple
from starlette.middleware.authentication import AuthenticationError
from starlette.requests import HTTPConnection
from starlette.authentication import (
    AuthenticationBackend,
    AuthCredentials,
)
from starlette.middleware.authentication import (
    AuthenticationMiddleware as BaseAuthenticationMiddleware,
)

from config.config import config
from config.logger_config import logger


class BaseData:
    def __init__(self, user_id: int, role: str, client_id: int, username: str, token: str):
        self.id_client_user = user_id
        self.role = role
        self.token = token  # New token returned to the client
        self.client_id = client_id
        self.username = username


    def __str__(self):
        return f"User ID: {self.id_client_user}, Role: {self.role}, Client ID: {self.client_id}, Username: {self.username}"


class OneAuthBackend(AuthenticationBackend):
    """Auth Backend para FastAPI con validación de token JWT."""

    def __init__(self, excluded_urls: List[str] = None):
        """
        Args:
            excluded_urls (List[str]): Routes excluded from authentication.

        """
        self.excluded_urls = [] if excluded_urls is None else excluded_urls

    def generate_new_token(self, payload: dict) -> str:
        """
        Generate a new JWT token with an updated expiration time.

        Args:
            payload (dict): JWT payload.
        """
        logger.info("MIDDLEWARE: Generating new token")
        payload["exp"] = datetime.utcnow() + timedelta(
            minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )  # New expiration time
        return jwt.encode(payload, config.CIVA_SECRET_KEY, algorithm=config.CIVA_ALGORITHM)

    async def authenticate(self, conn: HTTPConnection) -> Tuple[AuthCredentials, BaseData]:
        """
        Authenticate the request and return the credentials and user.

        Args:
            conn (HTTPConnection): HTTP Connection object.

        """
        logger.info(f"MIDDLEWARE: Authenticating request to {conn.url.path}")
        # Excluded Public Routes
        if conn.url.path in self.excluded_urls:
            return AuthCredentials(scopes=[]), None

        # Authorization Header
        auth_header = conn.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.error("MIDDLEWARE: No token provided in the Authorization header")
            raise AuthenticationError("No token provided in the Authorization header")

        token = auth_header.split(" ")[1]

        try:
            # payload = jwt.decode(token, config.CIVA_SECRET_KEY, algorithms=[config.CIVA_ALGORITHM], options={"verify_aud": False})

            payload = jwt.decode(
            token,
            config.CIVA_SECRET_KEY,
            algorithms=[config.CIVA_ALGORITHM],
            audience="tuClienteWeb"  # Ajusta esto al valor correcto
            )

            user_id = payload.get("nameid")
            role = payload.get("http://schemas.microsoft.com/ws/2008/06/identity/claims/role", "Unknown")
            areas = payload.get("areas")
            client_id = payload.get("cliente")
            username = payload.get("nombrePersonal")

            data = BaseData(
                user_id=user_id,
                role=areas,
                client_id=client_id,
                username=username,
                token=token
            )

            scopes = payload.get("scopes", [])

            logger.info("MIDDLEWARE: Authenticated user successfully")
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")
        except jwt.PyJWTError:
            logger.error(f"MIDDLEWARE: Invalid token provided")
            raise AuthenticationError(f"Invalid token provided")

        return AuthCredentials(scopes=scopes), data


class AuthenticationMiddleware(BaseAuthenticationMiddleware):
    pass
