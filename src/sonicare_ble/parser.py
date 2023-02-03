"""Parser for Sonicare BLE advertisements."""
from __future__ import annotations

import logging
import time

from dataclasses import dataclass
from enum import Enum, auto

from bleak import BLEDevice
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import SensorDeviceClass, SensorUpdate, Units
from sensor_state_data.enum import StrEnum

from .const import (
    BRUSHING_UPDATE_INTERVAL_SECONDS,
    CHARACTERISTIC_BATTERY,
    CHARACTERISTIC_BRUSHING_TIME,
    CHARACTERISTIC_CURRENT_TIME,
    CHARACTERISTIC_STATE,
    NOT_BRUSHING_UPDATE_INTERVAL_SECONDS,
    TIMEOUT_RECENTLY_BRUSHING,
    CHARACTERISTIC_BRUSH_USAGE,
    CHARACTERISTIC_BRUSH_LIFETIME,
    CHARACTERISTIC_SERIAL_NUMBER,
    CHARACTERISTIC_STRENGTH,
    CHARACTERISTIC_MODE,
    SONICARE_ADVERTISMENT_UUID
)

_LOGGER = logging.getLogger(__name__)


class SonicareSensor(StrEnum):

    BRUSHING_TIME = "brushing_time"
    CURRENT_TIME = "current_time"
    TOOTHBRUSH_STATE = "toothbrush_state"
    MODE = "mode"
    SIGNAL_STRENGTH = "signal_strength"
    BATTERY_PERCENT = "battery_percent"
    BRUSH_TYPE = "brush_type"
    BRUSH_STRENGTH = "brush_strength"
    BRUSH_HEAD_LIFETIME = "brush_head_lifetime"
    BRUSH_HEAD_USAGE = "brush_head_usage"
    BRUSH_HEAD_PERCENTAGE = "brush_head_percentage"

class SonicareBinarySensor(StrEnum):
    BRUSHING = "brushing"


class Models(Enum):

    HX6340 = auto()
    HX992X = auto()
    HX9990 = auto()


@dataclass
class ModelDescription:

    device_type: str
    modes: dict[int, str]


KIDS_MODES = {
    0: "none"
}

EXPERT_CLEAN_MODES = {
    120: "clean",
    200: "gun health",
    180: "deep clean+",
}

DIAMOND_CLEAN_MODES = EXPERT_CLEAN_MODES | {160: "white+"}

PRESTIGE_MODES = DIAMOND_CLEAN_MODES | {210: "sensitive"}

DEVICE_TYPES = {
    Models.HX6340: ModelDescription(
        device_type="HX6340",
        modes=KIDS_MODES
    ),
    Models.HX992X: ModelDescription(
        device_type="HX992X",
        modes=DIAMOND_CLEAN_MODES
    ),
    Models.HX9990: ModelDescription(
        device_type="HX9990",
        modes=PRESTIGE_MODES
    )
}

STRENGTH = {
    0: "low",
    1: "medium",
    2: "high"
}

STATES = {
    0: "off",
    1: "standby",
    2: "run",
    3: "charge",
    4: "shutdown",
    6: "validate",
    7: "lightsout",
}


SONICARE_MANUFACTURER = 477


BYTES_TO_MODEL = {
    b"\x062k": Models.HX6340,
    b"\x2a24": Models.HX992X,
    b"\x9999": Models.HX9990,
}

class SonicareBluetoothDeviceData(BluetoothData):
    """Data for Sonicare BLE sensors."""

    def __init__(self) -> None:
        super().__init__()
        # If this is True, we are currently brushing or were brushing as of the last advertisement data
        self._brushing = False
        self._last_brush = 0.0

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.debug("Parsing Sonicare BLE advertisement data: %s", service_info)
        manufacturer_data = service_info.manufacturer_data
        service_uuids = service_info.service_uuids
        address = service_info.address
        _LOGGER.debug(
            "Parsing Sonicare BLE advertisement manufacturer data: %s",
            manufacturer_data,
        )
        correct_device = False
        for service_uuid in service_uuids:
            _LOGGER.debug(
                "Parsing Sonicare BLE uuid: %s",
                service_uuid,
            )
            if SONICARE_ADVERTISMENT_UUID in service_uuid:
                correct_device = True

        if not correct_device:
            return None
#        if SONICARE_MANUFACTURER not in manufacturer_data:
#            return None
        #data = manufacturer_data[SONICARE_MANUFACTURER]
        self.set_device_manufacturer("Philips Sonicare")
        #_LOGGER.debug("Parsing Sonicare sensor: %s", data)
        #msg_length = len(data)
        #_LOGGER.debug("Message length: %s", msg_length)
        #if msg_length not in (9, 999):
        #    return
        # model = BYTES_TO_MODEL.get(device_bytes, Models.HX6340)
        model = Models.HX992X
        model_info = DEVICE_TYPES[model]
        self.set_device_type(model_info.device_type)
        name = f"{model_info.device_type} {short_address(address)}"
        self.set_device_name(name)
        self.set_title(name)

    def poll_needed(
        self, service_info: BluetoothServiceInfo, last_poll: float | None
    ) -> bool:
        """
        This is called every time we get a service_info for a device. It means the
        device is working and online.
        """
        _LOGGER.debug("poll_needed called")
        if last_poll is None:
            return True
        update_interval = NOT_BRUSHING_UPDATE_INTERVAL_SECONDS
        if (
            self._brushing
            or time.monotonic() - self._last_brush <= TIMEOUT_RECENTLY_BRUSHING
        ):
            update_interval = BRUSHING_UPDATE_INTERVAL_SECONDS
        return last_poll > update_interval

    async def async_poll(self, ble_device: BLEDevice) -> SensorUpdate:
        """
        Poll the device to retrieve any values we can't get from passive listening.
        """
        _LOGGER.debug("async_poll")
        client = await establish_connection(
            BleakClientWithServiceCache, ble_device, ble_device.address
        )
        for service in client.services:
            _LOGGER.debug("Service uuid=%s handle=%s", service.uuid, service.handle)
            for characteristic in service.characteristics:
                try:
                    value_char = client.services.get_characteristic(characteristic.uuid)
                    value_payload = await client.read_gatt_char(value_char)
                    _LOGGER.error(
                        "Characteristic uuid=%s handle=%s ValueChar=%s ValuePayload=%s",
                        characteristic.uuid,
                        characteristic.handle,
                        value_char,
                        value_payload,
                    )
                except Exception:
                    _LOGGER.debug("Exception reading characteristic")

        try:
            brush_usage_char = client.services.get_characteristic(CHARACTERISTIC_BRUSH_USAGE)
            brush_usage_payload = await client.read_gatt_char(brush_usage_char)

            brush_lifetime_char = client.services.get_characteristic(CHARACTERISTIC_BRUSH_LIFETIME)
            brush_lifetime_payload = await client.read_gatt_char(brush_lifetime_char)

            mode_char = client.services.get_characteristic(CHARACTERISTIC_MODE)
            mode_payload = await client.read_gatt_char(mode_char)

            strength_char = client.services.get_characteristic(CHARACTERISTIC_STRENGTH)
            strength_payload = await client.read_gatt_char(strength_char)

            battery_char = client.services.get_characteristic(CHARACTERISTIC_BATTERY)
            battery_payload = await client.read_gatt_char(battery_char)

            brushing_time_char = client.services.get_characteristic(
                CHARACTERISTIC_BRUSHING_TIME
            )
            brushing_time_payload = await client.read_gatt_char(brushing_time_char)

            state_char = client.services.get_characteristic(CHARACTERISTIC_STATE)
            state_payload = await client.read_gatt_char(state_char)
            tb_state = STATES.get(state_payload[0], f"unknown state {state_payload[0]}")

            current_time_char = client.services.get_characteristic(
                CHARACTERISTIC_CURRENT_TIME
            )
            current_time_payload = await client.read_gatt_char(current_time_char)
            current_time_epoch = int.from_bytes(current_time_payload, "little")
            current_time_stamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time_epoch))
        finally:
            _LOGGER.error("Unable to get data in async_poll")
            await client.disconnect()
        self.update_sensor(
            str(SonicareSensor.BRUSHING_TIME),
            None,
            int.from_bytes(brushing_time_payload, "little"),
            None,
            "Brushing time",
        )
        self.update_sensor(
            str(SonicareSensor.BATTERY_PERCENT),
            Units.PERCENTAGE,
            battery_payload[0],
            SensorDeviceClass.BATTERY,
            "Battery",
        )

        self.update_sensor(
            str(SonicareSensor.TOOTHBRUSH_STATE),
            None,
            tb_state,
            None,
            "Toothbrush State",
        )

        self.update_sensor(
            str(SonicareSensor.CURRENT_TIME),
            None,
            current_time_stamp,
            None,
            "Toothbrush current time",
        )

        self.update_sensor(
            str(SonicareSensor.BRUSH_HEAD_LIFETIME),
            None,
            int.from_bytes(brush_lifetime_payload, "little"),
            None,
            "Toothbrush head total lifetime"
        )

        self.update_sensor(
            str(SonicareSensor.BRUSH_HEAD_USAGE),
            None,
            int.from_byte(brush_usage_payload, "little"),
            None,
            "Toothbrush head usage"
        )

        self.update_sensor(
            str(SonicareSensor.MODE),
            None,
            mode_payload,
            None,
            "Toothbrush current mode"
        )

        self.update_sensor(
            str(SonicareSensor.BRUSH_STRENGTH),
            None,
            int.from_byte(strength_payload, "little"),
            None,
            "Toothbrush current strength"
        )
        return self._finish_update()
