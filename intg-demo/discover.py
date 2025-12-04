"""Demo Device Discovery Module.

This module is a placeholder for device discovery functionality.
The demo integration does not use discovery since there is no real device
to discover - the user simply enters an IP address during setup.

In a real integration, this module would implement device discovery
using protocols like:
- mDNS (Multicast DNS) for local network discovery
- SSDP (Simple Service Discovery Protocol) for UPnP devices
- SDDP (Simple Device Discovery Protocol)
- Custom discovery protocols specific to the device

:license: Mozilla Public License Version 2.0, see LICENSE for more details.
"""

# The demo integration does not implement discovery.
# See the setup.py module for the manual device configuration flow.
#
# Example of what discovery would look like for a real device:
#
# from ucapi_framework import DiscoveredDevice
# from ucapi_framework.discovery import MDNSDiscovery
#
# class DemoDiscovery(MDNSDiscovery):
#     """Discover demo devices on the local network."""
#
#     def parse_mdns_service(self, service_info: Any) -> DiscoveredDevice | None:
#         """Parse mDNS response into DiscoveredDevice."""
#         # Extract device info from service_info
#         # Return DiscoveredDevice with identifier, name, address, etc.
#         pass
