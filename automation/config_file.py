from nornir.plugins.functions.text import print_result
from automation.helper import start_nornir, TenantNode
from automation.ipam_calls import (dc_access_vlans, device_trunks,
                                   dc_vlans, get_outside_vrf,
                                   dc_fw_prefixes, get_prefixes, get_pat_ip)
import yaml


data = {}

def dc_access_params(task, tenant):
    temp = {}
    vlans = dc_access_vlans(tenant, task.host['site'])
    trunks = device_trunks(f'{task.host.name}', "mza-enc")
    temp['vlans'] = vlans
    temp['trunks'] = trunks
    data[task.host.name] = temp


def dc_agg_params(task, tenant):
    vlans = dc_vlans(tenant, task.host['site'])
    trunks = device_trunks(f'{task.host.name}', "dc-fw")
    vrfs, interfaces = get_prefixes(tenant, f'{task.host["asset_tag"]}')
    outside_vrf = get_outside_vrf(tenant)
    print(vlans, trunks, vrfs, interfaces)
    temp = {}
    temp['vlans'] = vlans
    temp['trunks'] = trunks
    temp['vrfs'] = vrfs
    temp['interfaces'] = interfaces
    temp['outside_vrf'] = outside_vrf
    data[task.host.name] = temp


def dc_fw_params(task, tenant):
    trunks = device_trunks(f'{task.host.name}', "agg")
    interfaces = dc_fw_prefixes(tenant)
    pat_ip = get_pat_ip(tenant)
    temp = {}
    temp['trunks'] = trunks
    temp['interfaces'] = interfaces
    temp['pat_ip'] = pat_ip
    data[task.host.name] = temp


def main():
    #infra = 'mza-infra'
    #tenant = 'commvault'
    #site = 'mv1'
    infra = 'lab'
    tenant = 'ipam'
    site = 'gns3'
    nr = start_nornir(infra)
    h1 = nr.filter(role="dc-access", site=site)
    h1.run(task=dc_access_params, tenant=tenant)
    h2 = nr.filter(role="dc-aggregation", site=site)
    r2 = h2.run(task=dc_agg_params, tenant=tenant)
    print_result(r2)
    h3 = nr.filter(role="dc-fw", site=site)
    h3.run(task=dc_fw_params, tenant=tenant)
    noalias_dumper = yaml.dumper.SafeDumper
    noalias_dumper.ignore_aliases = lambda self, data: True
    with open(f'/home/wamer/netops/automation/files/{tenant}.yaml', 'w') as f:
        yaml.dump(data, f, default_flow_style=False, Dumper=noalias_dumper)


if __name__ == '__main__':
    main()