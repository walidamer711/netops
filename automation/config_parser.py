from ciscoconfparse import CiscoConfParse
from nornir.plugins.functions.text import print_result
from nornir import InitNornir
from nornir.core.inventory import ConnectionOptions
from nornir.plugins.tasks import networking
import re, ipaddress, json, csv
import requests, ipaddress



NETBOX_API_ROOT = "http://172.20.22.99/api"
NETBOX_VM_ENDPOINT = "/virtualization/virtual-machines/"
cntx_prefix = {}
vrfs = []





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
    with open(f"backup/cntx/{cntx}.txt", "w") as f:
        f.write(r.result)


def vrfs_from_device():
    with open("backup/MV1_N7K_AGG_PE_01.txt", "r") as f:
        confile = f.read()
    parse = CiscoConfParse(confile.splitlines())
    print(parse)
    VRF_RE = re.compile(r'^vrf\scontext\s\S*\d*')


    for obj in parse.find_objects(VRF_RE):
        v = {}
        v['name'] = obj.re_match(r'vrf context (.+)')
        v['rd'] = "{}000".format(obj.re_match_iter_typed(r'^\s+rd\s(.+)', default='')[:-3])
        v['description'] = obj.re_match_iter_typed(r'^\s+description\s(.+)', default='')
        vrfs.append(v)
    keys = vrfs[0].keys()
    with open("files/vrf_list", "w") as f:
        dict_writer = csv.DictWriter(f, keys)
        dict_writer.writeheader()
        dict_writer.writerows(vrfs)
        json.dump(vrfs, f)


def cntx_from_device():
    with open("backup/MV1_5585_DC_ASA_01.txt", "r") as f:
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
    with open(f"backup/cntx/{cntx}.txt", "r") as f:
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
        x.append("{},Active,{},{},{}".format(str(ipaddress.ip_interface(sub).network),tenant,"MV1",vland_id))
        #print("{},Active,{},{}".format(str(ipaddress.ip_interface(sub).network),cntx,vland_id))
    cntx_prefix[f"{cntx}"] = prefix
    return x

def main():
    #print(get_tenant_from_vm("cntx-racks24-01"))
    cntx = cntx_from_device()
    for c in cntx:
        l1 = prefix_from_cntx(c)
        #print("{:#^20s}".format(""))
        for l in l1:
            print(l)

    #nr = start_nornir('mza-infra')
    #h = nr.filter(name='MV1_5585_DC_ASA_01')
    #for c in cntx:
    #    r = h.run(task=fw_cntx, cntx=c)
    #    print_result(r)



if __name__ == '__main__':
    main()
