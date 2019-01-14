from ciscoconfparse import CiscoConfParse
from nornir.plugins.functions.text import print_result
from nornir import InitNornir
from nornir.core.inventory import ConnectionOptions
from nornir.plugins.tasks import networking
import re, ipaddress, json, csv
import requests, ipaddress
from helper import start_nornir



NETBOX_API_ROOT = "http://172.20.22.99/api"
NETBOX_VM_ENDPOINT = "/virtualization/virtual-machines/"
NETBOX_VRFS_ENDPOINT = "/ipam/vrfs/"
cntx_prefix = {}



def form_headers():
    api_token = '49d66235f10e0d388f18e179e756d1d276b898bb'
    # api_token = os.environ.get("NETBOX_API_TOKEN")
    headers = {
        "Authorization": "Token {}".format(api_token),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    return headers


def get_tenant_from_vm(vm):
    headers = form_headers()
    query_params = {"name": vm}
    #vm here is the context name
    vms_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_VM_ENDPOINT,
        params=query_params, headers=headers
    ).json()
    for vm in vms_netbox_dict['results']:
        #print(vm['tenant'])
        if vm['tenant']:
            return vm['tenant']['name']
        else:
            return None

def get_tenant_from_vrf(vrf):
    headers = form_headers()
    query_params = {"name": vrf}
    VRFs_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_VRFS_ENDPOINT,
        params=query_params, headers=headers
    ).json()
    for v in VRFs_netbox_dict['results']:
        if v['tenant']:
            return v['tenant']['name']
        else:
            return None



def config_backup(task):
    r = task.run(task=networking.napalm_get, getters=["config"])
    with open(f"backup/{task.host.name}.txt", "w") as f:
        f.write(r.result['config']['running'])
    confile = r.result['config']['running']


def fw_config(task):
    r = task.run(task=networking.netmiko_send_command,
                 name="Loading Configuration on the device",
                 command_string="changeto system\n show run context")
    with open(f"backup/{task.host.name}.txt", "w") as f:
        f.write(r.result)


def fw_cntx(task, cntx):
    r = task.run(task=networking.netmiko_send_command,
                     name="Gather Configuration from the device",
                     command_string=f"changeto context {cntx}\n show run interface")
    with open(f"backup/mv2-cntx/{cntx}.txt", "w") as f:
        f.write(r.result)


def vrfs_from_device():
    with open("backup/MV1_N7K_AGG_PE_01.txt", "r") as f:
        confile = f.read()
    parse = CiscoConfParse(confile.splitlines())
    print(parse)
    VRF_RE = re.compile(r'^vrf\scontext\s\S*\d*')
    #VRF_RE = re.compile(r'^vrf\scontext\sVR184000')
    routes = []
    vrfs = []
    for obj in parse.find_objects(VRF_RE):
        v = {}
        v['name'] = obj.re_match(r'vrf context (.+)')
        v['rd'] = "{}000".format(obj.re_match_iter_typed(r'^\s+rd\s(.+)', default='')[:-3])
        v['description'] = obj.re_match_iter_typed(r'^\s+description\s(.+)', default='')
        vrfs.append(v)

    keys = vrfs[0].keys()
    with open("files/mv2_vrf_list", "w") as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(vrfs)
        json.dump(vrfs, f)


def pub_ips_from_device():
    with open("backup/MV2_N7K_AGG_PE_01.txt", "r") as f:
        confile = f.read()
    parse = CiscoConfParse(confile.splitlines())
    print(parse)
    VRF_RE = re.compile(r'^vrf\scontext\s\S*\d*')
    #VRF_RE = re.compile(r'^vrf\scontext\sVR184000')
    routes = []
    ips = []
    for obj in parse.find_objects(VRF_RE):
        v = {}
        vrf = obj.re_match(r'vrf context (.+)')
        #if get_tenant_from_vrf(vrf):
        tenant = get_tenant_from_vrf(vrf)
        route = obj.re_search_children(r'^\s+ip route\s(.+?)\s')
        for r in route:
            if not ipaddress.ip_network(r.re_match(r'^\s+ip route\s(.+?)\s')).is_private:
                if ipaddress.ip_network(r.re_match(r'^\s+ip route\s(.+?)\s')).prefixlen == 32:
                    ips.append("{},{},Active".format(r.re_match(r'^\s+ip route\s(.+?)\s'), tenant))
    #for ip in routes:
    #    if not ipaddress.ip_network(ip).is_private:
    #        ips.append(ip)
    return ips


def cntx_from_device():
    with open("backup/MV2-5585-DC-ASA-01.txt", "r") as f:
        confile = f.read()
    cntx_list = []
    parse = CiscoConfParse(confile.splitlines())
    print(parse)
    CNTX_RE = re.compile(r'^context\s\S*\d*')
    for obj in parse.find_objects(CNTX_RE):
        #print(obj.re_match(r'context (.+)'))
        cntx_list.append(obj.re_match(r'context (.+)'))
    return cntx_list


def prefix_from_cntx(cntx):
    with open(f"backup/mv2-cntx/{cntx}.txt", "r") as f:
        confile = f.read()
    tenant = get_tenant_from_vm(cntx)
    x = []
    prefix = []
    parse = CiscoConfParse(confile.splitlines())
    CNTX_RE = re.compile(r'^interface\sPort-channel11.\d*')
    for obj in parse.find_objects(CNTX_RE):
        vland_id = obj.re_match(r'^interface\sPort-channel11.(\d+)')
        nameif = obj.re_match_iter_typed(r'^\s+nameif\s(.+)', default='')
        subnet = obj.re_match_iter_typed(r'^\s+ip address\s(.+)', default='')
        sub = str(re.search(r'^(\S+)\s(\S+)', subnet).group(1)+"/"+re.search(r'^(\S+)\s(\S+)', subnet).group(2))
        prefix.append(str(ipaddress.ip_interface(sub).network))
        x.append("{},Active,{},{},{}".format(str(ipaddress.ip_interface(sub).network),tenant,"MV2",vland_id))
        #print("{},Active,{},{}".format(str(ipaddress.ip_interface(sub).network),cntx,vland_id))
    cntx_prefix[f"{cntx}"] = prefix
    return x

def main():
    '''
    workflow:
    - use nornir to connect to DCFW and run fw_config task and collect
    contexts configured from system context
    nr = start_nornir('mza-infra')
    h = nr.filter(name='MV2-5585-DC-ASA-01')
    h.run(task=fw_config)
    - parse the context info and get context list through cntx_from_device function
    cntx = cntx_from_device()
    - run nornir task fw_cntx aginsts DCFW and get each context interfaces configuration
    for c in cntx:
        r = h.run(task=fw_cntx, cntx=c)
    - for each context in the context list run prefix_from_cntx to get all prefixes under each context
    for c in cntx:
        l1 = prefix_from_cntx(c)
        #print("{:#^20s}".format(""))
        for l in l1:
            print(l)

    :return:
    '''
    #nr = start_nornir('mza-infra')
    #h = nr.filter(name='MV2_N7K_AGG_PE_01')
    #h.run(task=config_backup)
    #r = h.run(task=fw_config)
    #print_result(r)
    #cntx = cntx_from_device()
    #for c in cntx:
    #    print("{},mzamv2dcfw".format(c))
    #for c in cntx:
    #   r = h.run(task=fw_cntx, cntx=c)
    #   print_result(r)
    #for c in cntx:
    #    l1 = prefix_from_cntx(c)
    #    #print("{:#^20s}".format(""))
    #    for l in l1:
    #        print(l)
    #vrfs_from_device()
    #print(get_tenant_from_vrf('VR122000'))
    #print(pub_ips_from_device())
    for ip in pub_ips_from_device():
        #if ipaddress.ip_network(ip).prefixlen == 32:
        print(ip)





if __name__ == '__main__':
    main()
