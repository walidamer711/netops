from nornir import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking
from nornir.core.filter import F
from automation.helper import add_account


def fex_view_result(command, site):
    if site == "mv1":
        site1 = "mv1"
        site2 = "mv3"
    else:
        site1 = "mv2"
        site2 = "mv2"
    nr = InitNornir(config_file="/home/wamer/netops/automation/config.yaml")
    inv = nr.inventory.filter(F(has_fex=True) & F(site=site1) | F(has_fex=True) & F(site=site2))
    add_account(inv)
    hosts = nr.filter(F(has_fex=True) & F(site=site1) | F(has_fex=True) & F(site=site2))
    result = hosts.run(task=networking.netmiko_send_command, command_string=command, use_textfsm=True)
    return result

def main():
   #print_result(net_view_result('show fex'))
   result = fex_view_result('show fex', 'mv2')
   for r in result:
        print(result[r])

if __name__ == '__main__':
    main()