"""Remote entity module.

This module implements a minimal remote entity for testing the ucapi-framework.
It supports basic ON and OFF commands only.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging
from typing import Any

import ucapi
from ucapi import EntityTypes, Remote, StatusCodes, remote
from ucapi.remote import Attributes, Features
from ucapi.remote import States as RemoteStates

from device import DemoDevice
from const import DemoConfig
from ucapi_framework import create_entity_id, RemoteEntity, RemoteAttributes

_LOG = logging.getLogger(__name__)


class DemoRemote(RemoteEntity):
    """Representation of a Demo Remote entity."""

    def __init__(self, config_device: DemoConfig, device: DemoDevice):
        """Initialize the class."""
        self._device = device
        _LOG.debug("Demo Remote init")
        entity_id = create_entity_id(EntityTypes.REMOTE, config_device.identifier)
        features = [Features.ON_OFF]
        super().__init__(
            entity_id,
            f"{config_device.name} Remote",
            features,
            attributes={
                Attributes.STATE: RemoteStates.UNKNOWN,
            },
            cmd_handler=self.command_handler,  # type: ignore[arg-type]
        )

        if self._device is not None:
            self.subscribe_to_device(self._device)

    def map_entity_states(self, device_state: Any) -> RemoteStates:
        """Map media player device states to remote states."""
        match device_state:
            case s if s in (
                ucapi.media_player.States.ON,
                ucapi.media_player.States.PLAYING,
                ucapi.media_player.States.PAUSED,
                ucapi.media_player.States.BUFFERING,
            ):
                return RemoteStates.ON
            case ucapi.media_player.States.OFF:
                return RemoteStates.OFF
            case ucapi.media_player.States.STANDBY:
                return RemoteStates.OFF
            case _:
                return RemoteStates.UNKNOWN

    async def sync_state(self) -> None:
        """Sync entity state from device."""
        self.update(RemoteAttributes(STATE=self.map_entity_states(self._device.state)))

    async def command_handler(
        self, _entity: Remote, cmd_id: str, params: dict[str, Any] | None = None
    ) -> StatusCodes:
        """
        Remote entity command handler.

        Called by the integration-API if a command is sent to a configured remote entity.

        :param _entity: remote entity
        :param cmd_id: command
        :param params: optional command parameters
        :return: status code of the command request
        """
        _LOG.info(
            "Got %s command request: %s %s", self.id, cmd_id, params if params else ""
        )

        if self._device is None:
            _LOG.warning("No device instance for entity: %s", self.id)
            return ucapi.StatusCodes.SERVICE_UNAVAILABLE

        try:
            match cmd_id:
                case remote.Commands.ON:
                    _LOG.debug("Sending ON command to device")
                    await self._device.power_on()
                    return StatusCodes.OK
                case remote.Commands.OFF:
                    _LOG.debug("Sending OFF command to device")
                    await self._device.power_off()
                    return StatusCodes.OK
                case _:
                    _LOG.warning("Unsupported command: %s", cmd_id)
                    return StatusCodes.NOT_IMPLEMENTED

        except Exception as ex:  # pylint: disable=broad-except
            _LOG.error("Error executing remote command %s: %s", cmd_id, ex)
            return StatusCodes.BAD_REQUEST
