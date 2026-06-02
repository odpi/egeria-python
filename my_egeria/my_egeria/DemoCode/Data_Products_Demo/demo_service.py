""" python

   PDX-License-Identifier: Apache-2.0
   Copyright Contributors to the ODPi Egeria project.

   This file provides a a set of utility functions for my_egeria.
   All Egeria access is managed in this file

"""
import os
import time
from pyegeria import EgeriaTech

_last_auth_ts: float = 0.0
client = None
payload = None


def demo_service_init():
    global client, payload
    client = EgeriaTech(
        view_server=get_config()[1],
        platform_url=get_config()[0],
        user_id=get_config()[2],
        user_pwd=get_config()[3],
    )
    payload = None


def get_config():
    platform_url = os.getenv("EGERIA_PLATFORM_URL", "https: // localhost: 9443"),
    view_server = os.getenv("EGERIA_VIEW_SERVER", "qs-view-server"),
    user = os.getenv("EGERIA_USER", "erinoverview"),
    password = os.getenv("EGERIA_USER_PASSWORD", "secret"),
    token_ttl_seconds = int(os.getenv("EGERIA_TOKEN_TTL_SECONDS", "900"))

    Egeria_config: list = [platform_url,
                           view_server,
                           user,
                           password,
                           token_ttl_seconds]

    return Egeria_config

def access_egeria(self, payload) -> bool:
    # put in a timer and every 15 minutes (900 seconds) refresh the token.
    self.payload = payload
    try:
        self.log("Connecting to Egeria...")
        self.config = get_config()
        # create egeria client
        self.client = EgeriaTech(
            view_server=self.config[1],
            platform_url=self.config[0],
            user_id=self.config[2],
            user_pwd=self.config[3],
            )
        # generate egeria bearer token
        if self.token_expired():
            self.log("Refreshing Egeria token...")
            self.authenticate()
        #return True to signal client successfully connected to egeria
        if not self.client:
            self.log("Egeria connection failed")
            return False
        self.log("Egeria connection successful")
        return True
    except Exception as e:
        #return False to signal client failed to connect to egeria
        self.log(f"Egeria connection error: {e}")
        return False

def token_expired(self) -> bool:
    """check to verify if bearer token is still valid, we refresh every 15 minutes,
       at time of writing the Egeria default is 30 minutes, however, we use15 minuutes
       to be completely safe """
    if self._last_auth_ts <= 0:
        return True
    return (time.time() - self._last_auth_ts) >= self.config.token_ttl_seconds

def close_egeria_connection(self):
    if self.client:
        self.client.close_session()

def authenticate(self) -> None:
    if self.client and hasattr(self.client, "create_egeria_bearer_token"):
        self.client.create_egeria_bearer_token(self.config.user, self.config.password)
        self._last_auth_ts = time.time()
    else:
        self._client = None

def refresh_token(self) -> None:
    self.authenticate()

def find_collections(self) -> dict:
    if self.client and not self.token_expired():
        return self.get_collection_list()
    elif self.client:
        self.token_expired()
        return self._client.get_collection_list()
    else:
        rc = self.access_egeria(payload=self.payload)
        self.log(f"Egeria connection status: {rc}")
        return self.client.get_collection_list()

def egeria_login(self, payload) -> bool:
    self.payload = payload
    result = access_egeria(self, payload=self.payload)
    return result

