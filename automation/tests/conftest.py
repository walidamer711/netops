import pytest
from nornir import InitNornir
from decouple import config
from nornir.core.inventory import ConnectionOptions

@pytest.fixture(scope="session", autouse=True)
def nr():
    return InitNornir(core={"num_workers": 100},
                        logging={"file": "/home/wamer/netops/automation/nornir.log"},
                        inventory={"plugin": "nornir.plugins.inventory.netbox.NBInventory",
                                   "options": {"nb_url": "http://172.20.22.99",
                                               "nb_token": "49d66235f10e0d388f18e179e756d1d276b898bb",
                                               "filter_parameters": {"tenant": "mza-infra"}},
                                   "transform_function": add_conn_options})

def add_conn_options(host):
    host.username = config('username')
    host.password = config('password')
    host.connection_options["netmiko"] = ConnectionOptions(extras={'secret': config('secret')})