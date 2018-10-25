from nornir.core import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking, text
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


def get_fex_parents():
    headers = form_headers()
    query_params = {"tenant": "mza-infra", "tag": "fex"}
    r = requests.get(NETBOX_API_ROOT + NETBOX_DEVICES_ENDPOINT,
                     params=query_params, headers=headers)
    nb_devices = r.json()
    devices = {}
    for d in nb_devices["results"]:
        # Create temporary dict
        temp = {}
        # Add value for IP address
        if d.get("primary_ip", {}):
            temp["hostname"] = d["primary_ip"]["address"].split("/")[0]
        # Add values that don't have an option for 'slug'
        temp["serial"] = d["serial"]
        temp["vendor"] = d["device_type"]["manufacturer"]["name"]
        temp["asset_tag"] = d["asset_tag"]
        # Add values that do have an option for 'slug'
        temp["site"] = d["site"]["slug"]
        temp["role"] = d["device_role"]["slug"]
        temp["model"] = d["device_type"]["slug"]
        # Attempt to add 'platform' based of value in 'slug'
        temp["platform"] = d["platform"]["slug"] if d["platform"] else None
        temp["groups"] = ["nxos_group"]
        # Assign temporary dict to outer dict
        devices[d["name"]] = temp
    return devices


def load_hosts_file():
    with open('/home/wamer/netops/dashboard/inventory/hosts.yaml', 'w') as f:
        yaml.dump(get_fex_parents(), f, default_flow_style=False)

def add_account(inventory):
    for h in inventory.hosts:
        inventory.hosts[h].data.update(ACCOUNT)


def net_view_result(command):
    load_hosts_file()
    nr = InitNornir(config_file="/home/wamer/netops/dashboard/simple.yaml")
    add_account(nr.inventory)
    hosts = nr.filter(all)
    result = hosts.run(task=networking.netmiko_send_command, command_string=command, use_textfsm=True)
    return result

def main():
   print_result(net_view_result('show fex'))


if __name__ == '__main__':
    main()