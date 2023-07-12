import httpx as httpx
from loguru import logger

from port_ocean.clients.port.authentication import PortAuthentication
from port_ocean.clients.port.mixins.entities import EntityClientMixin
from port_ocean.clients.port.mixins.integrations import IntegrationClientMixin
from port_ocean.clients.port.types import (
    KafkaCreds,
)
from port_ocean.clients.port.utils import handle_status_code
from port_ocean.core.models import Blueprint
from port_ocean.exceptions.clients import KafkaCredentialsNotFound


class PortClient(EntityClientMixin, IntegrationClientMixin):
    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        integration_identifier: str,
        integration_type: str,
    ):
        self.api_url = f"{base_url}/v1"
        self.client = httpx.AsyncClient()
        self.auth = PortAuthentication(
            self.client,
            client_id,
            client_secret,
            self.api_url,
            integration_identifier,
            integration_type,
        )
        EntityClientMixin.__init__(self, self.auth, self.client)
        IntegrationClientMixin.__init__(self, self.auth, self.client)

    async def get_kafka_creds(self, silent: bool = False) -> KafkaCreds:
        logger.info("Fetching organization kafka credentials")
        response = await self.client.get(
            f"{self.api_url}/kafka-credentials", headers=await self.auth.headers()
        )
        if response.is_error:
            logger.error(f"Error getting kafka credentials, error: {response.text}")
        handle_status_code(silent, response)

        credentials = response.json().get("credentials")

        if credentials is None:
            raise KafkaCredentialsNotFound("No kafka credentials found")

        return credentials

    async def get_org_id(self) -> str:
        logger.info("Fetching organization id")

        response = await self.client.get(
            f"{self.api_url}/organization", headers=await self.auth.headers()
        )
        if response.is_error:
            logger.error(f"Error getting organization id, error: {response.text}")
            response.raise_for_status()

        return response.json()["organization"]["id"]

    async def get_blueprint(self, identifier: str) -> Blueprint:
        logger.info(f"Fetching blueprint with id: {identifier}")
        response = await self.client.get(
            f"{self.api_url}/blueprints/{identifier}",
            headers=await self.auth.headers(),
        )
        response.raise_for_status()
        return Blueprint.parse_obj(response.json()["blueprint"])