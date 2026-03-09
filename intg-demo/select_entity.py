"""Select entity module for the Demo integration.

This module implements a select entity that lets the user pick a TV show
from the full list, making it the currently playing title on the device.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

import logging
from typing import Any

import ucapi
from ucapi import EntityTypes, StatusCodes
from ucapi.select import Attributes, Commands, States

from device import DemoDevice
from const import DemoConfig, TV_SHOWS
from ucapi_framework import SelectEntity, SelectAttributes, create_entity_id

_LOG = logging.getLogger(__name__)


class DemoSelect(SelectEntity):
    """Demo TV show select entity.

    Lets the user pick any show from the full TV_SHOWS list.
    The chosen show becomes the active media title on the device,
    reflected immediately on the media player and remote entities
    via push_update → sync_state.
    """

    def __init__(self, config_device: DemoConfig, device: DemoDevice):
        """Initialize the TV show select entity."""
        self._device = device
        entity_id = create_entity_id(EntityTypes.SELECT, config_device.identifier)

        _LOG.debug("Initializing demo select entity: %s", entity_id)

        super().__init__(
            entity_id,
            f"{config_device.name} TV Show",
            attributes={
                Attributes.STATE: States.UNKNOWN,
                Attributes.OPTIONS: [],
                Attributes.CURRENT_OPTION: "",
            },
            cmd_handler=self.select_cmd_handler,
        )

        if device is not None:
            self.subscribe_to_device(device)

    async def sync_state(self) -> None:
        """Sync entity state from device."""
        self.update(
            SelectAttributes(
                STATE=States.ON
                if self._device.state.value != "OFF"
                else States.UNAVAILABLE,
                CURRENT_OPTION=self._device.media_title or "",
                OPTIONS=list(TV_SHOWS),
            )
        )

    async def select_cmd_handler(
        self,
        _entity: Any,
        cmd_id: str,
        params: dict[str, Any] | None,
        _websocket: Any = None,
    ) -> StatusCodes:
        """Handle select entity commands.

        :param _entity: Select entity (unused)
        :param cmd_id: Command identifier
        :param params: Optional command parameters
        :return: Status code
        """
        _LOG.info(
            "Got %s command request: %s %s", self.id, cmd_id, params if params else ""
        )

        if self._device is None:
            _LOG.warning("No device instance for entity: %s", self.id)
            return ucapi.StatusCodes.SERVICE_UNAVAILABLE

        match cmd_id:
            case Commands.SELECT_OPTION:
                if not params or "option" not in params:
                    return StatusCodes.BAD_REQUEST
                option = params["option"]
                if option not in TV_SHOWS:
                    _LOG.warning("Unknown show option: %s", option)
                    return StatusCodes.BAD_REQUEST
                await self._device.select_show(option)
                return StatusCodes.OK

            case Commands.SELECT_FIRST:
                await self._device.select_first_show()
                return StatusCodes.OK

            case Commands.SELECT_LAST:
                await self._device.select_last_show()
                return StatusCodes.OK

            case Commands.SELECT_NEXT:
                await self._device.select_next_show()
                return StatusCodes.OK

            case Commands.SELECT_PREVIOUS:
                await self._device.select_previous_show()
                return StatusCodes.OK

            case _:
                _LOG.warning("Unsupported command: %s", cmd_id)
                return StatusCodes.NOT_IMPLEMENTED
