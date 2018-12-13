from nornir import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking, text
from nornir.plugins.functions.text import print_result
from helper import start_nornir
from ipam_calls import (dc_access_vlans, device_trunks,
                        dc_vlans, get_outside_vrf,
                        dc_fw_prefixes, get_prefixes, get_pat_ip)


def dc_access_template(task, tenant):
    vlans = dc_access_vlans(tenant, task.host['site'])
    trunks = device_trunks(f'{task.host.name}', "mza-enc")
    r = task.run(task=text.template_file,
                 name="DC Access Configuration",
                 template="dc_access.j2",
                 path=f"/home/wamer/netops/automation/templates/cisco",
                 vlans=vlans, trunks=trunks)


def dc_agg_template(task, tenant):
    vlans = dc_vlans(tenant, task.host['site'])
    trunks = device_trunks(f'{task.host.name}', "dc-fw")
    vrfs, interfaces = get_prefixes(tenant, f'{task.host["asset_tag"]}')
    outside_vrf = get_outside_vrf(tenant)
    r1 = task.run(task=text.template_file,
                 name="DC Aggregation Configuration",
                 template="dc_agg.j2",
                 path=f"/home/wamer/netops/automation/templates/cisco",
                 cust=tenant, vlans=vlans, trunks=trunks, vrfs=vrfs, interfaces=interfaces)

    r2 = task.run(task=text.template_file,
                 name="Outside VRF Configuration",
                 template="int_agg.j2",
                 path=f"/home/wamer/netops/automation/templates/cisco",
                 cust=tenant, vrf=outside_vrf)


def dc_fw_template(task, tenant):
    trunks = device_trunks(f'{task.host.name}', "agg")
    interfaces = dc_fw_prefixes(tenant)
    r1 = task.run(task=text.template_file,
                  name="Firewall System Context Configuration",
                  template="sys_fw.j2",
                  path=f"/home/wamer/netops/automation/templates/cisco",
                  interfaces=interfaces, cust=tenant)

    pat_ip = get_pat_ip(tenant)
    r2 = task.run(task=text.template_file,
                 name="Base Configuration",
                 template="dc_fw.j2",
                 path=f"/home/wamer/netops/automation/templates/cisco",
                 interfaces=interfaces, trunk=trunks[0], cust=tenant,
                 site=task.host['site'], pat_ip=pat_ip)




def main():
    #infra = 'mza-infra'
    #tenant = 'commvault'
    #site = 'mv1'
    infra = 'lab'
    tenant = 'ipam'
    site = 'gns3'
    nr = start_nornir(infra)
    h1 = nr.filter(role="dc-access", site=site)
    result = h1.run(task=dc_access_template, tenant=tenant)
    print_result(result)
    h2 = nr.filter(role="dc-aggregation", site=site)
    result = h2.run(task=dc_agg_template, tenant=tenant)
    print_result(result)
    h3 = nr.filter(role="dc-fw", site=site)
    result = h3.run(task=dc_fw_template, tenant=tenant)
    print_result(result)

if __name__ == '__main__':
    main()