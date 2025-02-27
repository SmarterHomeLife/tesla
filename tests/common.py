"""Common methods used across tests for Tesla."""

from datetime import datetime
from unittest.mock import patch

from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_DOMAIN,
    CONF_TOKEN,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry
from teslajsonpy.car import TeslaCar
from teslajsonpy.const import AUTH_DOMAIN
from teslajsonpy.energy import SolarPowerwallSite, SolarSite

from custom_components.tesla_custom.const import CONF_EXPIRATION, DOMAIN as TESLA_DOMIN

from .const import TEST_ACCESS_TOKEN, TEST_TOKEN, TEST_USERNAME, TEST_VALID_EXPIRATION
from .mock_data import car as car_mock_data, energysite as energysite_mock_data


def setup_mock_controller(mock_controller):
    """Setup a mock controller with mock data."""

    instance = mock_controller.return_value

    instance.is_car_online.return_value = True
    instance.get_last_update_time.return_value = datetime.now()
    instance.get_last_update_time.return_value = datetime.now()
    instance.update_interval.return_value = 660

    instance.get_tokens.return_value = {
        "refresh_token": TEST_TOKEN,
        "access_token": TEST_ACCESS_TOKEN,
        "expiration": TEST_VALID_EXPIRATION,
    }

    instance.generate_car_objects.return_value = {
        car_mock_data.VIN: TeslaCar(
            car_mock_data.VEHICLE,
            mock_controller.return_value,
            car_mock_data.VEHICLE_DATA,
        )
    }

    instance.generate_energysite_objects.return_value = {
        12345: SolarSite(
            mock_controller.api,
            energysite_mock_data.ENERGYSITE_SOLAR,
            energysite_mock_data.SITE_CONFIG_SOLAR,
            energysite_mock_data.SITE_DATA,
        ),
        67890: SolarPowerwallSite(
            mock_controller.api,
            energysite_mock_data.ENERGYSITE_BATTERY,
            energysite_mock_data.SITE_CONFIG_POWERWALL,
            energysite_mock_data.BATTERY_DATA,
            energysite_mock_data.BATTERY_SUMMARY,
        ),
    }


async def setup_platform(hass: HomeAssistant, platform: str) -> MockConfigEntry:
    """Set up the Tesla platform."""

    mock_entry = MockConfigEntry(
        domain=TESLA_DOMIN,
        title=TEST_USERNAME,
        data={
            CONF_USERNAME: TEST_USERNAME,
            CONF_ACCESS_TOKEN: TEST_ACCESS_TOKEN,
            CONF_TOKEN: TEST_TOKEN,
            CONF_EXPIRATION: TEST_VALID_EXPIRATION,
            CONF_DOMAIN: AUTH_DOMAIN,
        },
        options=None,
    )

    mock_entry.add_to_hass(hass)

    with (
        patch("custom_components.tesla_custom.PLATFORMS", [platform]),
        patch(
            "custom_components.tesla_custom.TeslaAPI", autospec=True
        ) as mock_controller,
    ):
        setup_mock_controller(mock_controller)
        assert await async_setup_component(hass, TESLA_DOMIN, {})
    await hass.async_block_till_done()

    return mock_entry, mock_controller
