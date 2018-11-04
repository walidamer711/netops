from nornir.core import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking, text
from nornir.core.filter import F
import json, csv
import yaml
import requests
from decouple import config

NETBOX_API_ROOT = "http://172.20.22.99/api"
NETBOX_DEVICES_ENDPOINT = "/dcim/devices/"

ACCOUNT = {"username": config('username'), "password": config('password')}


def form_headers():
    api_token = '49d66235f10e0d388f18e179e756d1d276b898bb'
    # api_token = os.environ.get("NETBOX_API_TOKEN")
    headers = {
        "Authorization": "Token {}".format(api_token),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    return headers


def add_account(inventory):
    for h in inventory.hosts:
        inventory.hosts[h].data.update(ACCOUNT)


def net_view_result(command):
    nr = InitNornir(config_file="/home/wamer/netops/dashboard/config.yaml")
    inv = nr.inventory.filter(F(has_fex=True) & F(site="mv1") | F(has_fex=True) & F(site="mv3"))
    add_account(inv)
    hosts = nr.filter(F(has_fex=True) & F(site="mv1") | F(has_fex=True) & F(site="mv3"))
    result = hosts.run(task=networking.netmiko_send_command, command_string=command, use_textfsm=True)
    return result

def main():
   #print_result(net_view_result('show fex'))
   result = net_view_result('show fex')
   for r in result:
        print(result[r])

if __name__ == '__main__':
    main()