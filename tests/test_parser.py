from unittest import mock

import pytest
from bleak import BLEDevice
from bluetooth_sensor_state_data import BluetoothServiceInfo, SensorUpdate
from sensor_state_data import (
    BinarySensorDescription,
    BinarySensorValue,
    DeviceKey,
    SensorDescription,
    SensorDeviceClass,
    SensorDeviceInfo,
    SensorValue,
    Units,
)

from sonicare_ble.parser import SonicareBluetoothDeviceData

# 2023-01-29 09:17:16.610 DEBUG (MainThread) [homeassistant.components.bluetooth.manager] badkamerlamp (78:21:84:4f:6d:1c) [connectable]: 24:E5:AA:1A:70:A6 AdvertisementData(local_name='Sonicare4Kids', manufacturer_data={477: b'\x00\x1b\x00\xa6p\x1a\xaa\xe5$'}, service_uuids=['477ea600-a260-11e4-ae37-0002a5d50001'], tx_power=-127, rssi=-61) match: set()
# 2023-01-29 09:22:16.344 DEBUG (MainThread) [homeassistant.components.bluetooth.manager] badkamerlamp (78:21:84:4f:6d:1c) [connectable]: 24:E5:AA:47:AD:CB AdvertisementData(local_name='Sonicare4Kids', manufacturer_data={477: b'\x00\x1b\x00\xcb\xadG\xaa\xe5$'}, service_uuids=['477ea600-a260-11e4-ae37-0002a5d50001'], tx_power=-127, rssi=-82) match: set()

SONICARE_DATA_1 = BluetoothServiceInfo(
    name="24:E5:AA:1A:70:A6",
    address="24:E5:AA:1A:70:A6",
    rssi=-61,
    manufacturer_data={477: b"\x00\x1b\x00\xa6p\x1a\xaa\xe5$"},
    service_uuids=["477ea600-a260-11e4-ae37-0002a5d50001"],
    service_data={},
    source="local",
)
SONICARE_DATA_2 = BluetoothServiceInfo(
    name="24:E5:AA:47:AD:CB",
    address="24:E5:AA:47:AD:CB",
    rssi=-82,
    manufacturer_data={477: b"\x00\x1b\x00\xcb\xadG\xaa\xe5$"},
    service_uuids=["477ea600-a260-11e4-ae37-0002a5d50001"],
    service_data={},
    source="local",
)


def test_can_create():
    SonicareBluetoothDeviceData()


def test_dataset_1():
    parser = SonicareBluetoothDeviceData()
    service_info = SONICARE_DATA_1
    result = parser.update(service_info)
    assert result == SensorUpdate(
        title="Philips Sonicare for Kids",
        devices={
            None: SensorDeviceInfo(
                name="Sonicare4Kids",
                model="HX6340",
                manufacturer="Philips Sonicare",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="time", device_id=None): SensorDescription(
                device_key=DeviceKey(key="time", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="sector", device_id=None): SensorDescription(
                device_key=DeviceKey(key="sector", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="number_of_sectors", device_id=None): SensorDescription(
                device_key=DeviceKey(key="number_of_sectors", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="sector_timer", device_id=None): SensorDescription(
                device_key=DeviceKey(key="sector_timer", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="toothbrush_state", device_id=None): SensorDescription(
                device_key=DeviceKey(key="toothbrush_state", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="pressure", device_id=None): SensorDescription(
                device_key=DeviceKey(key="pressure", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="mode", device_id=None): SensorDescription(
                device_key=DeviceKey(key="mode", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
        },
        entity_values={
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal " "Strength",
                native_value=-63,
            ),
            DeviceKey(key="time", device_id=None): SensorValue(
                device_key=DeviceKey(key="time", device_id=None),
                name="Time",
                native_value=0,
            ),
            DeviceKey(key="sector", device_id=None): SensorValue(
                device_key=DeviceKey(key="sector", device_id=None),
                name="Sector",
                native_value="no " "sector",
            ),
            DeviceKey(key="number_of_sectors", device_id=None): SensorValue(
                device_key=DeviceKey(key="number_of_sectors", device_id=None),
                name="Number " "of " "sectors",
                native_value=4,
            ),
            DeviceKey(key="sector_timer", device_id=None): SensorValue(
                device_key=DeviceKey(key="sector_timer", device_id=None),
                name="Sector " "Timer",
                native_value=0,
            ),
            DeviceKey(key="toothbrush_state", device_id=None): SensorValue(
                device_key=DeviceKey(key="toothbrush_state", device_id=None),
                name="Toothbrush " "State",
                native_value="idle",
            ),
            DeviceKey(key="pressure", device_id=None): SensorValue(
                device_key=DeviceKey(key="pressure", device_id=None),
                name="Pressure",
                native_value="normal",
            ),
            DeviceKey(key="mode", device_id=None): SensorValue(
                device_key=DeviceKey(key="mode", device_id=None),
                name="Mode",
                native_value="daily " "clean",
            ),
        },
        binary_entity_descriptions={
            DeviceKey(key="brushing", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="brushing", device_id=None), device_class=None
            )
        },
        binary_entity_values={
            DeviceKey(key="brushing", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="brushing", device_id=None),
                name="Brushing",
                native_value=False,
            )
        },
        events={},
    )


def test_dataset_2():
    parser = SonicareBluetoothDeviceData()
    service_info = SONICARE_DATA_2
    result = parser.update(service_info)
    assert result == SensorUpdate(
        title="Philips Sonicare for Kids",
        devices={
            None: SensorDeviceInfo(
                name="Sonicare4Kids",
                model="HX6340",
                manufacturer="Philips Sonicare",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="sector", device_id=None): SensorDescription(
                device_key=DeviceKey(key="sector", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="toothbrush_state", device_id=None): SensorDescription(
                device_key=DeviceKey(key="toothbrush_state", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="sector_timer", device_id=None): SensorDescription(
                device_key=DeviceKey(key="sector_timer", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="mode", device_id=None): SensorDescription(
                device_key=DeviceKey(key="mode", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="time", device_id=None): SensorDescription(
                device_key=DeviceKey(key="time", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="pressure", device_id=None): SensorDescription(
                device_key=DeviceKey(key="pressure", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorDescription(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                device_class=SensorDeviceClass.SIGNAL_STRENGTH,
                native_unit_of_measurement=Units.SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            ),
            DeviceKey(key="number_of_sectors", device_id=None): SensorDescription(
                device_key=DeviceKey(key="number_of_sectors", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
        },
        entity_values={
            DeviceKey(key="sector", device_id=None): SensorValue(
                device_key=DeviceKey(key="sector", device_id=None),
                name="Sector",
                native_value="sector " "1",
            ),
            DeviceKey(key="toothbrush_state", device_id=None): SensorValue(
                device_key=DeviceKey(key="toothbrush_state", device_id=None),
                name="Toothbrush " "State",
                native_value="running",
            ),
            DeviceKey(key="sector_timer", device_id=None): SensorValue(
                device_key=DeviceKey(key="sector_timer", device_id=None),
                name="Sector " "Timer",
                native_value=0,
            ),
            DeviceKey(key="mode", device_id=None): SensorValue(
                device_key=DeviceKey(key="mode", device_id=None),
                name="Mode",
                native_value="daily " "clean",
            ),
            DeviceKey(key="time", device_id=None): SensorValue(
                device_key=DeviceKey(key="time", device_id=None),
                name="Time",
                native_value=0,
            ),
            DeviceKey(key="pressure", device_id=None): SensorValue(
                device_key=DeviceKey(key="pressure", device_id=None),
                name="Pressure",
                native_value="normal",
            ),
            DeviceKey(key="signal_strength", device_id=None): SensorValue(
                device_key=DeviceKey(key="signal_strength", device_id=None),
                name="Signal " "Strength",
                native_value=-63,
            ),
            DeviceKey(key="number_of_sectors", device_id=None): SensorValue(
                device_key=DeviceKey(key="number_of_sectors", device_id=None),
                name="Number " "of " "sectors",
                native_value=4,
            ),
        },
        binary_entity_descriptions={
            DeviceKey(key="brushing", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="brushing", device_id=None), device_class=None
            )
        },
        binary_entity_values={
            DeviceKey(key="brushing", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="brushing", device_id=None),
                name="Brushing",
                native_value=True,
            )
        },
        events={},
    )


@mock.patch("sonicare_ble.parser.establish_connection")
@pytest.mark.asyncio
async def test_async_poll(mock_establish_connection):
    parser = SonicareBluetoothDeviceData()
    device = BLEDevice(address="abc", name="test_device")
    mock_establish_connection.return_value.read_gatt_char.side_effect = [
        bytearray(b";\x00\x00\x00"),
        bytearray(b"\x01\x89\x7f\xbe\x04`\x7f\xbe\x047"),
    ]
    res = await parser.async_poll(device)
    assert (
        res.entity_values.get(DeviceKey("battery_percent")).native_value == 59
        and res.entity_values.get(DeviceKey("pressure")).native_value == "normal"
    )


def test_poll_needed_no_time():
    parser = SonicareBluetoothDeviceData()
    assert parser.poll_needed(None, None)


def test_poll_needed_brushing():
    parser = SonicareBluetoothDeviceData()
    parser._brushing = True
    assert parser.poll_needed(None, 61)


@mock.patch("sonicare_ble.parser.time")
def test_poll_needed_brushing_recently(mocked_time):
    parser = SonicareBluetoothDeviceData()
    mocked_time.monotonic.return_value = 5
    parser._brushing = False
    parser._last_brush = 0
    assert parser.poll_needed(None, 61)
