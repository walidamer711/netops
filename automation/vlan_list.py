from nornir import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking, text
import json, csv
import requests
from helper import start_nornir


NETBOX_API_ROOT = "http://172.20.22.99/api"
NETBOX_DEVICES_ENDPOINT = "/dcim/devices/"


def form_headers():
    api_token = '49d66235f10e0d388f18e179e756d1d276b898bb'
    # api_token = os.environ.get("NETBOX_API_TOKEN")
    headers = {
        "Authorization": "Token {}".format(api_token),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    return headers


def show_result(device, command):
    nr = start_nornir("mza-infra")
    host = nr.filter(name=device)
    result = host.run(task=networking.netmiko_send_command, command_string=command, use_textfsm=True)
    return result[device][0].result


def dc_vlan_list(h1,h2):
    r1 = show_result(h1, "show vlan")
    r2 = show_result(h2, "show vlan")
    l1 = []
    for r in r1:
        if r["name"] != "enet":
            l1.append(r)
    l2 = []
    for r in r2:
        if r["name"] != "enet":
            l2.append(r)
    check1 = set([int(d['vlan_id']) for d in l2])
    vlan_list = []
    for v in l1:
        if int(v['vlan_id']) not in check1:
            vlan_list.append(v)
    check2 = set([int(d['vlan_id']) for d in l1])
    for v in l2:
        if int(v['vlan_id']) not in check2:
            vlan_list.append(v)
    keys = vlan_list[0].keys()
    with open("vlan_list", "w") as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(vlan_list)
        json.dump(vlan_list, f)
    return len(vlan_list)


def diff(l1, l2):
    check = set([int(d['vlan_id']) for d in l2])
    return [d for d in l1 if int(d['vlan_id']) not in check]


def overlap(l1, l2):
    check = set([int(d['vlan_id']) for d in l2])
    return [d for d in l1 if int(d['vlan_id']) in check]


def vlan_diff(h1, h2):
    r1 = show_result(h1, "show vlan")
    r2 = show_result(h2, "show vlan")
    l1 = []
    for r in r1:
        if r["name"] != "enet":
            l1.append(r)
    l2 = []
    for r in r2:
        if r["name"] != "enet":
            l2.append(r)
    if len(l1) > len(l2):
        d = diff(l1, l2)
    else:
        d = diff(l2, l1)
    return len(d)


def main():
    #print(dc_vlan_list('MV2_N7K_AGG_PE_01', "MV2_N7K_SVC_PE_01"))
    #print(vlan_diff('MV2_N7K_SVC_PE_01','MV2_N7K_AGG_PE_01'))
    fexs = show_result('MV2_N7K_SVC_PE_01', "show fex")
    for fex in fexs:
        fex_num = fex['number']
        command = "show int status fex {}".format(fex_num)
        intfs = show_result('MV2_N7K_SVC_PE_01', command)
        down_list = []
        for intf in intfs:
            if intf['status'] == 'disabled':
                down_list.append(intf)
        print(len(down_list))

def test_netmiko(task):
    task.run(task=networking.netmiko_send_command, command_string="show version", use_textfsm=True)


if __name__ == '__main__':
    main()
