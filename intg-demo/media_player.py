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

import browser as demo_browser
import device
from const import DemoConfig
from ucapi.api_definitions import (
    BrowseOptions,
    BrowseResults,
    SearchOptions,
    SearchResults,
)
from ucapi_framework import (
    create_entity_id,
    MediaPlayerAttributes,
    MediaPlayerEntity,
)

_LOG = logging.getLogger(__name__)

# Features supported by the demo media player
# The demo device supports basic playback controls and media title display
FEATURES = [
    media_player.Features.ON_OFF,
    media_player.Features.TOGGLE,
    media_player.Features.PLAY_PAUSE,
    media_player.Features.MEDIA_TITLE,
    media_player.Features.BROWSE_MEDIA,
    media_player.Features.SEARCH_MEDIA,
    media_player.Features.PLAY_MEDIA,
]


class DemoMediaPlayer(MediaPlayerEntity):
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
                Attributes.STATE: media_player.States.UNKNOWN,
            },
            # Using STREAMING_BOX as the device class for the demo
            device_class=DeviceClasses.SPEAKER,
            cmd_handler=self.handle_command,
        )

        if device_instance is not None:
            self.subscribe_to_device(device_instance)

    async def sync_state(self) -> None:
        """Sync entity state from device."""
        attrs = self._device.get_media_player_attributes(self._device.identifier)
        self.update(
            MediaPlayerAttributes(
                STATE=self._device.state,
                MEDIA_TITLE=attrs.MEDIA_TITLE if attrs else None,
                MEDIA_IMAGE_URL=attrs.MEDIA_IMAGE_URL if attrs else None,
            )
        )

    async def handle_command(
        self,
        _entity: MediaPlayer,
        cmd_id: str,
        params: dict[str, Any] | None,
        _: Any | None = None,
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
        - PLAY_MEDIA: Play the show identified by params["media_id"]

        :param entity: The entity receiving the command (not used, same as self)
        :param cmd_id: The command identifier
        :param params: Optional command parameters
        :return: Status code indicating success or failure
        """
        _LOG.info("Received command: %s %s", cmd_id, params if params else "")

        if self._device is None:
            _LOG.warning("No device instance for entity: %s", self.id)
            return ucapi.StatusCodes.SERVICE_UNAVAILABLE

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

                case media_player.Commands.PLAY_MEDIA:
                    media_id = (params or {}).get("media_id", "")
                    if media_id:
                        await self._device.select_show(media_id)
                    else:
                        _LOG.warning("PLAY_MEDIA missing media_id parameter")
                        return ucapi.StatusCodes.BAD_REQUEST

                case _:
                    _LOG.warning("Unhandled command: %s", cmd_id)
                    return ucapi.StatusCodes.NOT_IMPLEMENTED

            return ucapi.StatusCodes.OK

        except Exception as ex:  # pylint: disable=broad-exception-caught
            _LOG.error("Error executing command %s: %s", cmd_id, ex)
            return ucapi.StatusCodes.BAD_REQUEST

    async def browse(self, options: BrowseOptions) -> BrowseResults | ucapi.StatusCodes:
        """
        Handle a browse-media request from the remote.

        Delegates to :mod:`browser` which walks the in-memory TV shows list.

        :param options: Browse options supplied by the remote (media_id, paging, …)
        :return: :class:`BrowseResults` on success, or a :class:`StatusCodes` on failure.
        """
        _LOG.debug("browse called: media_id=%s", options.media_id)
        try:
            return demo_browser.browse(options)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            _LOG.error("Error browsing media: %s", ex)
            return ucapi.StatusCodes.SERVER_ERROR

    async def search(self, options: SearchOptions) -> SearchResults | ucapi.StatusCodes:
        """
        Handle a search-media request from the remote.

        Performs a case-insensitive substring match on the TV shows list.

        :param options: Search options supplied by the remote (query, paging, …)
        :return: :class:`SearchResults` on success, or a :class:`StatusCodes` on failure.
        """
        _LOG.debug("search called: query=%s", options.query)
        try:
            return demo_browser.search(options)
        except Exception as ex:  # pylint: disable=broad-exception-caught
            _LOG.error("Error searching media: %s", ex)
            return ucapi.StatusCodes.SERVER_ERROR
