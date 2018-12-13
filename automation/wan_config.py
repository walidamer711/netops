from nornir import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking, text
from automation.ipam_calls import get_wan_vrf
from automation.helper import start_nornir


def wan_agg_config(task, tenant):
    wan_vrf = get_wan_vrf(tenant)


def wan_pe_config(task, tenant):
    wan_vrf = get_wan_vrf(tenant)


def main():
    infra = 'lab'
    tenant = 'ipam'
    site = 'gns3'

    nr = start_nornir(infra)
    h2 = nr.filter(role="dc-aggregation", site=site)
    result = h2.run(task=wan_pe_config, tenant=tenant)
    print_result(result)


if __name__ == '__main__':
    main()