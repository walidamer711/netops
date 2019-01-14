from nornir import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking, text
from automation.ipam_calls import get_wan_vrf
from automation.helper import start_nornir


def wan_agg_config(task, tenant):
    wan_vrf = get_wan_vrf(tenant, f'{task.host["asset_tag"]}')


def wan_pe_config(task, tenant):
    wan_vrf = get_wan_vrf(tenant, f'{task.host["asset_tag"]}')
    r = task.run(task=text.template_file,
                 name="Base Configuration",
                 template="wan_pe.j2",
                 path=f"/home/wamer/netops/automation/templates/cisco",
                 vrf=wan_vrf)
    task.host["config"] = r.result
    task.run(task=networking.napalm_configure,
             name="Loading Configuration on the device",
             replace=False,
             configuration=task.host["config"])
    return wan_vrf, task.host["asset_tag"]


def main():
    infra = 'lab'
    tenant = 'ipam'
    site = 'gns3'

    nr = start_nornir(infra)
    h2 = nr.filter(role="wan-router", site=site)
    result = h2.run(task=wan_pe_config, tenant=tenant)
    print_result(result)


if __name__ == '__main__':
    main()