"""Demo Integration Driver.

This is the main entry point for the demo integration driver. It initializes
the driver, sets up logging, and starts the integration API.

This demo integration serves as:
- A testing area for new developers learning the ucapi-framework
- A validation tool for testing framework changes
- An example of how to implement a complete integration

The demo device:
- Exposes a media_player entity
- Polls every 30 seconds and updates the media title with a random TV show
- Responds to PLAY_PAUSE by cycling to a new random TV show
- Requires no real hardware or network connectivity

:copyright: (c) 2025 by Unfolded Circle ApS.
:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import asyncio
import logging
import os

from const import DemoConfig
from device import DemoDevice
from media_player import DemoMediaPlayer
from setup import DemoSetupFlow
from ucapi_framework import BaseConfigManager, BaseIntegrationDriver, get_config_path


async def main():
    """Start the Demo integration driver."""
    logging.basicConfig()

    # Configure logging level from environment variable
    level = os.getenv("UC_LOG_LEVEL", "DEBUG").upper()
    logging.getLogger("driver").setLevel(level)
    logging.getLogger("media_player").setLevel(level)
    logging.getLogger("device").setLevel(level)
    logging.getLogger("setup_flow").setLevel(level)

    # Initialize the integration driver with the demo device and media player
    driver = BaseIntegrationDriver(
        device_class=DemoDevice, entity_classes=[DemoMediaPlayer]
    )

    # Configure the device config manager with DemoConfig
    driver.config_manager = BaseConfigManager(
        get_config_path(driver.api.config_dir_path),
        driver.on_device_added,
        driver.on_device_removed,
        config_class=DemoConfig,
    )

    # Register all configured devices from config file
    await driver.register_all_configured_devices()

    # Set up device setup flow - no discovery needed for the demo device
    # The setup flow only requires an IP address input
    setup_handler = DemoSetupFlow.create_handler(driver, discovery=None)

    # Initialize the API with the driver configuration
    await driver.api.init("driver.json", setup_handler)

    # Keep the driver running
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
