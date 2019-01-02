from decouple import config
from nornir import InitNornir
from nornir.core.inventory import ConnectionOptions

LAB_ACCOUNT = {"username": 'admin', "password": 'admin', "secret": "admin"}


def add_account_lab(inventory):
    for h in inventory.hosts:
        inventory.hosts[h].username = LAB_ACCOUNT['username']
        inventory.hosts[h].password = LAB_ACCOUNT['password']


def start_nornir(tenant):
    nr = InitNornir(core={"num_workers": 100},
                    logging={"file": "/home/wamer/netops/automation/nornir.log"},
                    inventory={"plugin": "nornir.plugins.inventory.netbox.NBInventory",
                               "options": {"nb_url": "http://172.20.22.99",
                                           "nb_token": "49d66235f10e0d388f18e179e756d1d276b898bb",
                                           "filter_parameters": {"tenant": tenant}},
                               "transform_function": add_conn_options})
    return nr


def add_conn_options(host):
    host.username = config('username')
    host.password = config('password')
    host.connection_options["netmiko"] = ConnectionOptions(extras={'secret': config('secret')})

