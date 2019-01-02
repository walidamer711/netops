from decouple import config
from nornir import InitNornir
from nornir.core.inventory import ConnectionOptions

LAB_ACCOUNT = {"username": 'admin', "password": 'admin', "secret": "admin"}
#ACCOUNT = {"username": config('username'), "password": config('password')}


def add_account_lab(inventory):
    for h in inventory.hosts:
        inventory.hosts[h].username = LAB_ACCOUNT['username']
        inventory.hosts[h].password = LAB_ACCOUNT['password']


#def add_account(inventory):
#    for h in inventory.hosts:
#        inventory.hosts[h].username = ACCOUNT['username']
#        inventory.hosts[h].password = ACCOUNT['password']


def start_nornir(tenant):
    nr = InitNornir(core={"num_workers": 100},
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


class TenantNode:

    nb_url = "http://172.20.22.99"
    nb_token = "49d66235f10e0d388f18e179e756d1d276b898bb"

    def __init__(self, infra):
        self.infra = infra

    def startNornir(self):
        nr = InitNornir(core={"num_workers": 100},
                        inventory={"plugin": "nornir.plugins.inventory.netbox.NBInventory",
                                   "options": {"nb_url": self.nb_url,
                                               "nb_token": self.nb_token,
                                               "filter_parameters": {"tenant": self.infra}},
                                   "transform_function": self.add_conn_options})
        return nr

    def add_conn_options(self, host):
        host.username = config('username')
        host.password = config('password')
        host.connection_options["netmiko"] = ConnectionOptions(extras={'secret': config('secret')})
