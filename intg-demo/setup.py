"""Demo Setup Flow Module.

This module handles the demo device setup and configuration process.
It provides a simple form for entering an IP address.

The setup is simplified for the demo - only an IP address is required.
The device ID and name are auto-generated.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging
import uuid
from typing import Any

from const import DemoConfig
from ucapi import IntegrationSetupError, RequestUserInput, SetupError
from ucapi_framework import BaseSetupFlow

_LOG = logging.getLogger(__name__)

# Simple setup form - only requires an IP address
# The device name and ID are auto-generated for simplicity
_DEMO_INPUT_SCHEMA = RequestUserInput(
    {"en": "Demo Device Setup"},
    [
        {
            "id": "info",
            "label": {
                "en": "Setup Demo Device",
            },
            "field": {
                "label": {
                    "value": {
                        "en": (
                            "Enter an IP address to set up the demo device. "
                            "This is a simulated device for testing the ucapi-framework. "
                            "The IP address doesn't need to be reachable - it's just used "
                            "as a placeholder identifier."
                        ),
                    }
                }
            },
        },
        {
            "field": {"text": {"value": "192.168.1.100"}},
            "id": "address",
            "label": {
                "en": "IP Address",
            },
        },
    ],
)


class DemoSetupFlow(BaseSetupFlow[DemoConfig]):
    """
    Setup flow for the demo integration.

    Handles demo device configuration with a simple IP address input.
    The device ID and name are auto-generated to demonstrate how a real
    integration might handle device discovery and identification.
    """

    def get_manual_entry_form(self) -> RequestUserInput:
        """
        Return the manual entry form for demo device setup.

        :return: RequestUserInput with a simple IP address field
        """
        return _DEMO_INPUT_SCHEMA

    async def query_device(
        self, input_values: dict[str, Any]
    ) -> DemoConfig | SetupError | RequestUserInput:
        """
        Create demo device configuration from user input.

        This method simulates what would happen in a real integration:
        - Connect to the device
        - Retrieve device info (serial number, model, etc.)
        - Generate a unique identifier
        - Create the device configuration

        For the demo, we auto-generate the ID and name based on the IP address.

        :param input_values: Dictionary containing the IP address from the form
        :return: DemoConfig on success, SetupError on failure
        """
        # Extract the IP address from form values
        address = input_values.get("address", "").strip()

        # Validate required field
        if not address:
            _LOG.warning("Address is required, re-displaying form")
            return _DEMO_INPUT_SCHEMA

        _LOG.debug("Setting up demo device with address: %s", address)

        try:
            # ================================================================
            # NOTE: In a real integration, you would:
            # 1. Connect to the device at the given address
            # 2. Query the device API for its information
            # 3. Retrieve the unique identifier (serial number, MAC address, etc.)
            # 4. Get the device name/model
            #
            # Example:
            # client = DeviceClient(address)
            # await client.connect()
            # device_info = await client.get_device_info()
            # identifier = device_info.get("serial_number")
            # name = device_info.get("name", f"Device ({address})")
            # await client.disconnect()
            # ================================================================

            # For the demo, auto-generate the identifier and name
            # Using a short UUID suffix to make it unique but readable
            short_id = str(uuid.uuid4())[:8]
            identifier = f"demo_{address.replace('.', '_')}_{short_id}"

            # Auto-generate a friendly name
            name = f"Demo ({address})"

            _LOG.info("Created demo device - ID: %s, Name: %s", identifier, name)

            return DemoConfig(
                identifier=identifier,
                name=name,
                address=address,
            )

        except ConnectionError as ex:
            _LOG.error("Connection refused to %s: %s", address, ex)
            return SetupError(IntegrationSetupError.CONNECTION_REFUSED)

        except TimeoutError as ex:
            _LOG.error("Connection timeout to %s: %s", address, ex)
            return SetupError(IntegrationSetupError.TIMEOUT)

        except Exception as ex:
            _LOG.error("Failed to set up demo device at %s: %s", address, ex)
            return SetupError(IntegrationSetupError.CONNECTION_REFUSED)
