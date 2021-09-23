import pytest

from labgrid.resource import Resource, NetworkSerialPort
from labgrid.resource.remote import RemoteNetworkInterface
from labgrid.driver import Driver, SerialDriver, NetworkInterfaceDriver
from labgrid.strategy import Strategy
from labgrid.binding import StateError


class ResourceA(Resource):
    pass


class DriverA(Driver):
    bindings = {"res": ResourceA}

    @Driver.check_bound
    def get_export_vars(self):
        return {
            "a": "b",
        }


class StrategyA(Strategy):
    bindings = {
        "drv": DriverA,
    }


def test_export(target):
    ra = ResourceA(target, "resource")
    d = DriverA(target, "driver")
    s = StrategyA(target, "strategy")

    exported = target.export()
    assert exported == {
        "LG__DRV_A": "b",
    }

    target.activate(d)
    with pytest.raises(StateError):
        d.get_export_vars()


class StrategyB(Strategy):
    bindings = {
        "drv": DriverA,
    }

    def prepare_export(self):
        return {
            self.drv: "custom_name",
        }


def test_export_custom(target):
    ra = ResourceA(target, "resource")
    d = DriverA(target, "driver")
    s = StrategyB(target, "strategy")

    exported = target.export()
    assert exported == {
        "LG__CUSTOM_NAME_A": "b",
    }


def test_export_network_serial(target):
    NetworkSerialPort(target, None, host='testhost', port=12345, speed=115200)
    SerialDriver(target, None)

    exported = target.export()
    assert exported == {
        'LG__SERIALDRIVER_HOST': 'testhost',
        'LG__SERIALDRIVER_PORT': '12345',
        'LG__SERIALDRIVER_PROTOCOL': 'rfc2217',
        'LG__SERIALDRIVER_SPEED': '115200'
    }


def test_export_remote_network_interface(target):
    RemoteNetworkInterface(target, None, host='testhost', ifname='wlan0')
    NetworkInterfaceDriver(target, "netif")

    exported = target.export()
    assert exported == {
        'LG__NETIF_HOST': 'testhost',
        'LG__NETIF_IFNAME': 'wlan0'
    }
