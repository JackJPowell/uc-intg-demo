"""Demo Device Module.

This module implements a demo device for testing the ucapi-framework.
It simulates a media player device that randomly cycles through TV show
names as the media title.

This serves as a testing area for new developers and for validating
the ucapi-framework after changes.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging
import random
from asyncio import AbstractEventLoop

from const import DemoConfig, TV_SHOWS
from ucapi import media_player
from ucapi_framework import (
    BaseConfigManager,
    MediaPlayerAttributes,
    PollingDevice,
    BaseIntegrationDriver,
)

_LOG = logging.getLogger(__name__)

# Polling interval in seconds - the demo device polls every 30 seconds
POLL_INTERVAL = 30


class DemoDevice(PollingDevice):
    """
    Demo device class for testing the ucapi-framework.

    This device simulates a media player that:
    - Polls every 30 seconds and updates the media title with a random TV show
    - Responds to PLAY_PAUSE by cycling to a random TV show
    - Inherits from PollingDevice to demonstrate polling functionality

    This is useful for:
    - Testing the ucapi-framework without real hardware
    - Learning how to implement a device integration
    - Validating framework changes
    """

    def __init__(
        self,
        device_config: DemoConfig,
        loop: AbstractEventLoop | None,
        config_manager: BaseConfigManager | None = None,
        driver: BaseIntegrationDriver | None = None,
    ) -> None:
        """
        Initialize the demo device.

        :param device_config: Configuration for this device
        :param loop: Event loop for async operations
        :param config_manager: Configuration manager instance
        """
        super().__init__(
            device_config=device_config,
            loop=loop,
            poll_interval=POLL_INTERVAL,
            config_manager=config_manager,
            driver=driver,
        )

        # Initialize device state tracking
        self._power_state: media_player.States = media_player.States.OFF
        self._media_title: str = ""

        # Attribute dict keyed by device_id (str) — supplemental media player fields
        self._media_player_attributes: dict[str, MediaPlayerAttributes] = {}

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def identifier(self) -> str:
        """Return the device identifier."""
        return self._device_config.identifier

    @property
    def name(self) -> str:
        """Return the device name."""
        return self._device_config.name

    @property
    def address(self) -> str | None:
        """Return the device address."""
        return self._device_config.address

    @property
    def state(self) -> media_player.States:
        """Return the current power state."""
        return self._power_state

    @property
    def media_title(self) -> str:
        """Return the current media title."""
        return self._media_title

    @property
    def log_id(self) -> str:
        """Return a log identifier for debugging."""
        return self.name if self.name else self.identifier

    # =========================================================================
    # Typed attribute accessors (keyed by device_id)
    # =========================================================================

    def get_media_player_attributes(self, device_id: str) -> MediaPlayerAttributes | None:
        """Return current MediaPlayer attributes for the given device_id."""
        return self._media_player_attributes.get(device_id)

    # =========================================================================
    # PollingDevice Implementation
    # =========================================================================


    async def establish_connection(self) -> None:
        """
        Establish initial connection to the demo device.

        For the demo device, this is a no-op since there's no real device.
        In a real implementation, this would:
        - Connect to the device API
        - Authenticate if needed
        - Retrieve initial state

        NOTE: In a real integration, you would retrieve device info here:
        # response = await self._client.get_device_info()
        # self._device_id = response.get("serial_number")
        # self._model = response.get("model")
        """
        _LOG.info(
            "[%s] Demo device connection established (simulated) at %s",
            self.log_id,
            self.address,
        )
        # Set initial state to ON when connecting
        self._power_state = media_player.States.ON
        self._select_random_show()
        self._media_player_attributes[self.identifier] = MediaPlayerAttributes(
            MEDIA_TITLE=self._media_title,
            MEDIA_IMAGE_URL="https://avatars.githubusercontent.com/u/102359576?s=200&v=4",
        )
        self.push_update()

    async def poll_device(self) -> None:
        """
        Poll the demo device for status updates.

        Called every 30 seconds by the PollingDevice base class.
        Simulates polling by selecting a random TV show and updating the media title.

        NOTE: In a real integration, you would query the device API here:
        # response = await self._client.get_status()
        # self._power_state = PowerState(response.get("power"))
        # self._media_title = response.get("now_playing", {}).get("title", "")
        """
        _LOG.debug("[%s] Polling demo device...", self.log_id)

        # Only update media title if device is ON or PLAYING
        if self._power_state in (media_player.States.ON, media_player.States.PLAYING):
            self._select_random_show()
            _LOG.info(
                "[%s] Poll update - Now showing: %s", self.log_id, self._media_title
            )
            attrs = self._media_player_attributes.get(self.identifier)
            if attrs:
                attrs.MEDIA_TITLE = self._media_title
            self.push_update()

    # =========================================================================
    # Power Control
    # =========================================================================

    async def power_on(self) -> None:
        """Turn on the demo device."""
        _LOG.debug("[%s] Powering on", self.log_id)
        self._power_state = media_player.States.ON
        self._select_random_show()
        attrs = self._media_player_attributes.get(self.identifier)
        if attrs:
            attrs.MEDIA_TITLE = self._media_title
        self.push_update()

    async def power_off(self) -> None:
        """Turn off the demo device."""
        _LOG.debug("[%s] Powering off", self.log_id)
        self._power_state = media_player.States.OFF
        self._media_title = ""
        attrs = self._media_player_attributes.get(self.identifier)
        if attrs:
            attrs.MEDIA_TITLE = self._media_title
        self.push_update()

    async def power_toggle(self) -> None:
        """Toggle the demo device power state."""
        _LOG.debug("[%s] Toggling power", self.log_id)
        if self._power_state in (
            media_player.States.ON,
            media_player.States.PLAYING,
            media_player.States.PAUSED,
        ):
            await self.power_off()
        else:
            await self.power_on()

    # =========================================================================
    # Playback Control
    # =========================================================================

    async def play_pause(self) -> None:
        """
        Handle play/pause command.

        When pressed, this cycles to a random TV show and updates the media title.
        This demonstrates the framework's ability to handle commands and emit updates.
        """
        _LOG.debug("[%s] Play/Pause pressed", self.log_id)

        if self._power_state == media_player.States.OFF:
            # Turn on if off
            await self.power_on()
            self._power_state = media_player.States.PLAYING
        elif self._power_state == media_player.States.PAUSED:
            # Resume playing and pick a new show
            self._power_state = media_player.States.PLAYING
            self._select_random_show()
        elif self._power_state in (
            media_player.States.ON,
            media_player.States.PLAYING,
            media_player.States.PAUSED,
        ):
            # Toggle between playing and paused, pick new show when resuming
            if self._power_state == media_player.States.PLAYING:
                self._power_state = media_player.States.PAUSED
            else:
                self._power_state = media_player.States.PLAYING
            self._select_random_show()

        _LOG.info(
            "[%s] Now showing: %s (state: %s)",
            self.log_id,
            self._media_title,
            self._power_state,
        )
        attrs = self._media_player_attributes.get(self.identifier)
        if attrs:
            attrs.MEDIA_TITLE = self._media_title
        self.push_update()

    # =========================================================================
    # Helper Methods
    # =========================================================================

    async def select_show(self, title: str) -> None:
        """Directly set the current media title to the given TV show."""
        _LOG.debug("[%s] Show selected: %s", self.log_id, title)
        self._media_title = title
        # Ensure the device is playing when a show is picked
        if self._power_state not in (
            media_player.States.ON,
            media_player.States.PLAYING,
        ):
            self._power_state = media_player.States.ON
        attrs = self._media_player_attributes.get(self.identifier)
        if attrs:
            attrs.MEDIA_TITLE = self._media_title
        self.push_update()

    async def select_first_show(self) -> None:
        """Select the first show in the TV_SHOWS list."""
        await self.select_show(TV_SHOWS[0])

    async def select_last_show(self) -> None:
        """Select the last show in the TV_SHOWS list."""
        await self.select_show(TV_SHOWS[-1])

    async def select_next_show(self) -> None:
        """Advance to the next show in the TV_SHOWS list, wrapping around."""
        try:
            idx = TV_SHOWS.index(self._media_title)
        except ValueError:
            idx = -1
        await self.select_show(TV_SHOWS[(idx + 1) % len(TV_SHOWS)])

    async def select_previous_show(self) -> None:
        """Go back to the previous show in the TV_SHOWS list, wrapping around."""
        try:
            idx = TV_SHOWS.index(self._media_title)
        except ValueError:
            idx = 0
        await self.select_show(TV_SHOWS[(idx - 1) % len(TV_SHOWS)])

    def _select_random_show(self) -> None:
        """Select a random TV show from the list."""
        # Avoid selecting the same show twice in a row
        available_shows = [show for show in TV_SHOWS if show != self._media_title]
        self._media_title = random.choice(available_shows)


