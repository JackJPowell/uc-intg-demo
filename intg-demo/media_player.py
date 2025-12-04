"""Demo Media Player Entity.

This module defines the media player entity for the demo device. It handles
playback controls and demonstrates how to implement a media player integration.

This serves as a testing area for new developers and for validating
the ucapi-framework after changes.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging
from typing import Any

import ucapi
from ucapi import MediaPlayer, media_player, EntityTypes
from ucapi.media_player import DeviceClasses, Attributes

import device
from const import DemoConfig
from ucapi_framework import create_entity_id

_LOG = logging.getLogger(__name__)

# Features supported by the demo media player
# The demo device supports basic playback controls and media title display
FEATURES = [
    media_player.Features.ON_OFF,
    media_player.Features.TOGGLE,
    media_player.Features.PLAY_PAUSE,
    media_player.Features.MEDIA_TITLE,
]


class DemoMediaPlayer(MediaPlayer):
    """
    Demo Media Player entity for testing the ucapi-framework.

    This entity demonstrates:
    - Basic power control (on/off/toggle)
    - Play/pause functionality that cycles through random TV shows
    - Media title display updated via polling and user interaction

    The media player responds to PLAY_PAUSE commands by selecting a random
    TV show and displaying it as the media title.
    """

    def __init__(self, config_device: DemoConfig, device_instance: device.DemoDevice):
        """
        Initialize the demo media player entity.

        :param config_device: Device configuration from setup
        :param device_instance: The demo device instance to control
        """
        self._device = device_instance
        entity_id = create_entity_id(EntityTypes.MEDIA_PLAYER, config_device.identifier)

        _LOG.debug("Initializing demo media player entity: %s", entity_id)

        super().__init__(
            entity_id,
            config_device.name,
            FEATURES,
            attributes={
                Attributes.STATE: device_instance.state,
                Attributes.MEDIA_TITLE: device_instance.media_title,
            },
            # Using STREAMING_BOX as the device class for the demo
            device_class=DeviceClasses.STREAMING_BOX,
            cmd_handler=self.handle_command,
        )

    async def handle_command(
        self, entity: MediaPlayer, cmd_id: str, params: dict[str, Any] | None
    ) -> ucapi.StatusCodes:
        """
        Handle media player commands from the remote.

        This method is called by the integration API when a command is sent
        to this media player entity.

        Supported commands:
        - ON: Turn on the demo device
        - OFF: Turn off the demo device
        - TOGGLE: Toggle power state
        - PLAY_PAUSE: Cycle to a random TV show and update media title

        :param entity: The media player entity receiving the command
        :param cmd_id: The command identifier
        :param params: Optional command parameters
        :return: Status code indicating success or failure
        """
        _LOG.info("Received command: %s %s", cmd_id, params if params else "")

        try:
            match cmd_id:
                case media_player.Commands.ON:
                    await self._device.power_on()

                case media_player.Commands.OFF:
                    await self._device.power_off()

                case media_player.Commands.TOGGLE:
                    await self._device.power_toggle()

                case media_player.Commands.PLAY_PAUSE:
                    # This is the main demo feature - cycles through random TV shows
                    await self._device.play_pause()

                case _:
                    _LOG.warning("Unhandled command: %s", cmd_id)
                    return ucapi.StatusCodes.NOT_IMPLEMENTED

            return ucapi.StatusCodes.OK

        except Exception as ex:
            _LOG.error("Error executing command %s: %s", cmd_id, ex)
            return ucapi.StatusCodes.BAD_REQUEST
