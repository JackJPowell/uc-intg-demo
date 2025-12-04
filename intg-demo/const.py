"""Constants for the Demo Integration.

This module contains configuration dataclasses and constants used throughout
the demo integration. This serves as a testing area for developers validating
the ucapi-framework.

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

from dataclasses import dataclass


# List of great TV shows to randomly cycle through as media titles
TV_SHOWS = [
    "Breaking Bad",
    "The Wire",
    "Game of Thrones",
    "The Sopranos",
    "Mad Men",
    "The Office",
    "Friends",
    "Seinfeld",
    "Stranger Things",
    "The Mandalorian",
    "Ted Lasso",
    "Succession",
    "Better Call Saul",
    "The Crown",
    "Chernobyl",
    "Fleabag",
    "Black Mirror",
    "Fargo",
    "True Detective",
    "Westworld",
]


@dataclass
class DemoConfig:
    """
    Demo device configuration dataclass.

    This dataclass holds all the configuration needed to identify a demo device.
    The address field simulates an IP address that would normally be used to
    connect to a real device.
    """

    identifier: str
    """Unique identifier of the device (auto-generated from address)."""

    name: str
    """Friendly name of the device for display purposes."""

    address: str
    """Simulated IP address of the demo device."""
