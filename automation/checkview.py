from nornir import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking, text
from nornir.core.filter import F
from automation.helper import start_nornir
from automation.ipam_calls import dc_join_vlans


def check_dc_vlan(tenant, site):
    vlan_list = dc_join_vlans(tenant)
    command = "show vlan id {}".format(vlan_list)
    nr = start_nornir('mza-infra')
    hosts = nr.filter(F(vlandomain__label=site))
    result = hosts.run(task=networking.netmiko_send_command, command_string=command)
    return result



def main():
    result = check_dc_vlan("ipam", "lab")
    print_result(result)

if __name__ == '__main__':
    main()