"""
Cognito M2M (Machine-to-Machine) authentication module.
Handles token acquisition and in-memory caching for M2M authentication flow.
"""

import logging
import threading
import time
from typing import Optional

import requests

from app.config import config

logger = logging.getLogger(__name__)


class CognitoM2MTokenCache:
    """
    In-memory cache for Cognito M2M tokens.
    Thread-safe implementation to handle concurrent access.
    """

    def __init__(self):
        """Initialize the token cache with lock for thread safety."""
        self._token: Optional[str] = None
        self._expires_at: float = 0
        self._lock = threading.RLock()
        self._buffer_seconds = 60  # Refresh token 60 seconds before expiration

    def set_token(self, token: str, expires_in: int) -> None:
        """
        Store token with expiration time.

        Args:
            token: Access token from Cognito
            expires_in: Token lifetime in seconds
        """
        with self._lock:
            self._token = token
            self._expires_at = time.time() + expires_in
            logger.debug(
                f"Token cached, expires in {expires_in} seconds "
                f"(at {self._expires_at})"
            )

    def get_token(self) -> Optional[str]:
        """
        Retrieve cached token if valid.

        Returns:
            Cached token if valid and not expired, None otherwise
        """
        with self._lock:
            if self._token and time.time() < (self._expires_at - self._buffer_seconds):
                return self._token
            return None

    def is_expired(self) -> bool:
        """
        Check if cached token is expired or about to expire.

        Returns:
            True if token is expired or will expire soon, False otherwise
        """
        with self._lock:
            return time.time() >= (self._expires_at - self._buffer_seconds)

    def clear(self) -> None:
        """Clear the cached token."""
        with self._lock:
            self._token = None
            self._expires_at = 0
            logger.debug("Token cache cleared")


# Global token cache instance
_token_cache = CognitoM2MTokenCache()


def get_m2m_token() -> Optional[str]:
    """
    Get a valid Cognito M2M access token.

    Uses in-memory cache to store tokens. If cached token is valid,
    it returns the cached token. Otherwise, it requests a new token from Cognito.

    Returns:
        Access token string if successful, None otherwise

    Raises:
        ValueError: If required Cognito configuration is missing
    """
    # Check if cached token is still valid
    cached_token = _token_cache.get_token()
    if cached_token:
        logger.debug("Using cached M2M token")
        return cached_token

    # Validate configuration
    if not all([config.COGNITO_DOMAIN, config.COGNITO_CLIENT_ID, config.COGNITO_CLIENT_SECRET]):
        logger.error(
            "Cognito configuration incomplete: COGNITO_DOMAIN, "
            "COGNITO_CLIENT_ID, and COGNITO_CLIENT_SECRET are required"
        )
        return None

    try:
        # Request new token from Cognito
        token_url = f"{config.COGNITO_DOMAIN}/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        payload = {
            "grant_type": "client_credentials",
            "client_id": config.COGNITO_CLIENT_ID,
            "client_secret": config.COGNITO_CLIENT_SECRET,
        }

        if config.COGNITO_SCOPE:
            payload["scope"] = config.COGNITO_SCOPE

        logger.debug(f"Requesting M2M token from {token_url}")

        response = requests.post(
            token_url,
            headers=headers,
            data=payload,
            timeout=30
        )
        response.raise_for_status()

        token_response = response.json()

        if "access_token" not in token_response:
            logger.error(f"Token response missing access_token: {token_response}")
            return None

        access_token = token_response["access_token"]
        expires_in = token_response.get("expires_in", 3600)  # Default 1 hour

        # Cache the token
        _token_cache.set_token(access_token, expires_in)

        logger.info(f"Successfully obtained M2M token (expires in {expires_in}s)")
        return access_token

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to obtain M2M token from Cognito: {e!s}", exc_info=True)
        return None
    except (ValueError, KeyError) as e:
        logger.error(f"Invalid token response from Cognito: {e!s}", exc_info=True)
        return None


def clear_token_cache() -> None:
    """
    Manually clear the token cache.
    Useful for force refresh or debugging.
    """
    _token_cache.clear()


def get_cached_token() -> Optional[str]:
    """
    Get the currently cached token without making a request.

    Returns:
        Cached token if available, None otherwise
    """
    return _token_cache.get_token()
