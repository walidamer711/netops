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
NETBOX_VLANS_ENDPOINT = "/ipam/vlans/"

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


def get_dc_vlans(tenant):
    headers = form_headers()
    query_params = {"tenant": tenant, "status": 2}

    vlans_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_VLANS_ENDPOINT,
        params=query_params, headers=headers
    ).json()
    l1 = []
    vlans = []
    for v in vlans_netbox_dict["results"]:
        # Create temporary dict
        temp = {}
        temp["name"] = v["name"]
        temp["id"] = v["vid"]
        l1.append(str(v["vid"]))
        temp["role"] = v["role"]["slug"]
        vlans.append(temp)
    x = (',').join(l1)
    return x


def check_dc_vlan(tenant, site):
    if site == "mv1":
        site1 = "mv1"
        site2 = "mv3"
    else:
        site1 = "mv2"
        site2 = "mv2"
    vlan_list = get_dc_vlans(tenant)
    command = "show vlan id {}".format(vlan_list)
    nr = InitNornir(config_file="/home/wamer/netops/dashboard/config.yaml")
    inv = nr.inventory.filter(F(dc_vlan_domain=True) & F(site=site1) | F(dc_vlan_domain=True) & F(site=site2))
    add_account(inv)
    hosts = nr.filter(F(dc_vlan_domain=True) & F(site=site1) | F(dc_vlan_domain=True) & F(site=site2))
    result = hosts.run(task=networking.netmiko_send_command, command_string=command, use_textfsm=True)
    return result



def main():
    print_result(check_dc_vlan("ipam", "mv2"))

if __name__ == '__main__':
    main()