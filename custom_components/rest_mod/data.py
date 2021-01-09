"""Support for RESTful API."""
import logging

import httpx

"""from homeassistant.helpers.httpx_client import get_async_client"""

DEFAULT_TIMEOUT = 10

_LOGGER = logging.getLogger(__name__)


class RestDataMod:
    """Class for handling the data retrieval."""

    def __init__(
        self,
        hass,
        method,
        resource,
        auth,
        headers,
        params,
        data,
        verify_ssl,
        timeout=DEFAULT_TIMEOUT,
        proxy_url=None,
    ):
        """Initialize the data object."""
        self._hass = hass
        self._method = method
        self._resource = resource
        self._auth = auth
        self._headers = headers
        self._params = params
        self._request_data = data
        self._timeout = timeout
        self._verify_ssl = verify_ssl
        self._async_client = None
        self.data = None
        self.headers = None

        if proxy_url is not None:
            self._proxies = {
                "http://": proxy_url,
                "https://": proxy_url,
            }
        else:
            self._proxies = None

    def set_payload(self, payload):
        """Set payload."""
        self._request_data = payload

    def set_url(self, url):
        """Set url."""
        self._resource = url

    async def async_update(self):
        """Get the latest data from REST service with provided method."""
        headers = {}
        if self._headers:
            for header_name, header_template in self._headers.items():
                headers[header_name] = header_template.async_render(parse_result=False)

        if not self._async_client:
            self._async_client = httpx.AsyncClient(verify=self._verify_ssl, proxies=self._proxies)

        _LOGGER.debug("Updating from %s", self._resource)
        try:
            response = await self._async_client.request(
                self._method,
                self._resource,
                headers=headers,
                params=self._params,
                auth=self._auth,
                data=self._request_data,
                timeout=self._timeout,
            )
            self.data = response.text
            self.headers = response.headers
        except httpx.RequestError as ex:
            _LOGGER.warning("Error fetching data: %s failed with %s", self._resource, ex)
            self.data = None
            self.headers = None
