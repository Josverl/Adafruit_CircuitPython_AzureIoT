# The MIT License (MIT)
#
# Copyright (c) 2019 Brent Rubell for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`Adafruit_AzureIoT`
================================================================================

Microsoft Azure IoT for CircuitPython

* Author(s): Brent Rubell

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
* Adafruit's ESP32SPI library: https://github.com/adafruit/Adafruit_CircuitPython_ESP32SPI
"""

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_AzureIoT.git"

AZURE_API_VER = "2018-06-30" # Azure URI API Version Identifier
AZURE_HTTP_ERROR_CODES = [400, 401, 404, 403, 412, 429, 500] # Azure HTTP Status Codes

class IOT_HUB:
    """
    Provides access to a Microsoft Azure IoT Hub.
    https://docs.microsoft.com/en-us/rest/api/iothub/
    """
    def __init__(self, wifi_manager, iot_hub_name, sas_token):
        """ Creates an instance of an Azure IoT Hub Client.
        :param wifi_manager: WiFiManager object from ESPSPI_WiFiManager.
        :param str iot_hub_name: Name of your IoT Hub.
        :param str sas_token: Azure IoT Hub SAS Token Identifier.
        """
        _wifi_type = str(type(wifi_manager))
        if 'ESPSPI_WiFiManager' in _wifi_type:
            self._wifi = wifi_manager
        else:
            raise TypeError("This library requires a WiFiManager object.")
        self._iot_hub_url = "https://{0}.azure-devices.net".format(iot_hub_name)
        self._sas_token = sas_token
        self._azure_header = {"Authorization":self._sas_token}

    @staticmethod
    def _parse_http_status(status_code, status_reason):
        """Parses HTTP Status, throws error based on Azure IoT Common Error Codes.
        :param int status_code: HTTP status code.
        :param str status_reason: Description of HTTP status.
        """
        for error in AZURE_HTTP_ERROR_CODES:
            if error == status_code:
                raise TypeError("Error {0}: {1}".format(status_code, status_reason))

    # HTTP Request Methods
    def _post(self, path, payload):
        response = self._wifi.post(
            path,
            json=payload,
            headers=self._azure_header)
        self._parse_http_status(response.status_code, response.reason)
        return response.json()

    def _get(self, path):
        response = self._wifi.get(
            path,
            headers=self._azure_header)
        self._parse_http_status(response.status_code, response.reason)
        return response.json()

    def _delete(self, path):
        response = self._wifi.delete(
            path,
            headers=self._azure_header)
        self._parse_http_status(response.status_code, response.reason)
        return response.json()

    def _patch(self, path, payload):
        response = self._wifi.patch(
            path,
            json=payload,
            headers=self._azure_header)
        self._parse_http_status(response.status_code, response.reason)
        return response.json()

    def _put(self, path, payload):
        response = self._wifi.put(
            path,
            json=payload,
            headers=self._azure_header)
        self._parse_http_status(response.status_code, response.reason)
        return response.json()

    # Device Messaging
    # D2C: Device-to-Cloud
    def send_device_message(self, device_id, message):
        """Sends a device-to-cloud message.
        :param string device_id: Device Identifier.
        :param string message: Message.
        """
        path = "{0}/devices/{1}/messages/events?api-version={2}".format(self._iot_hub_url,
                                                                        device_id, AZURE_API_VER)
        self._post(path, message)

    # TODO: Cloud-to-Device Communication

    # Device Twin
    def get_device_twin(self, device_id):
        """Returns a device twin
        :param str device_id: Device Identifier.
        """
        path = "{0}/twins/{1}?api-version={2}".format(self._iot_hub_url, device_id, AZURE_API_VER)
        return self._get(path)

    def update_device_twin(self, device_id, properties):
        """Updates tags and desired properties of a device twin.
        :param str device_id: Device Identifier.
        :param str properties: Device Twin Properties
        (https://docs.microsoft.com/en-us/rest/api/iothub/service/updatetwin#twinproperties)
        """
        path = "{0}/twins/{1}?api-version={2}".format(self._iot_hub_url, device_id, AZURE_API_VER)
        return self._patch(path, properties)

    def replace_device_twin(self, device_id, properties):
        """Replaces tags and desired properties of a device twin.
        :param str device_id: Device Identifier.
        :param str properties: Device Twin Properties.
        """
        path = "{0}/twins/{1}?api-version-{2}".format(self._iot_hub_url, device_id, AZURE_API_VER)
        return self._put(path, properties)

    # IoT Hub Service
    def get_devices(self):
        """Retrieve devices from the identity registry of your IoT hub.
        """
        path = "{0}/devices/?api-version={1}".format(self._iot_hub_url, AZURE_API_VER)
        return self._get(path)

    def get_device(self, device_id):
        """Retrieves a device from the identity registry of an IoT hub.
        :param str device_id: Device Identifier.
        """
        path = "{0}/devices/{1}?api-version={2}".format(self._iot_hub_url, device_id, AZURE_API_VER)
        return self._get(path)

    def delete_device(self, device_id):
        """Deletes a specified device_id from the identity register of an IoT Hub.
        :param str device_id: Device Identifier.
        """
        path = "{0}/devices/{1}?api-version={2}".format(self._iot_hub_url, device_id, AZURE_API_VER)
        self._delete(path)
