from nornir.core import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking, text


def show_result(device, command):
    nr = InitNornir(config_file="/home/wamer/netops/dashboard/config.yaml", dry_run=True)
    host = nr.filter(name=device)
    result = host.run(task=networking.netmiko_send_command, command_string=command, use_textfsm=True)
    return result[device][0].result

def main():
    r = show_result("MV1_N5K_DC_ACC_01", "show version")
    print(r)
    #nr = InitNornir(config_file="config.yaml", dry_run=True)
    #host = nr.filter(role="dc-access", site="mv1")
    #print_title("Playbook to configure the network")
    #result = host.run(task=test_netmike)
    #print_result(result)


def test_netmike(task):

    task.run(task=networking.netmiko_send_command, command_string="show version", use_textfsm=True)

if __name__ == '__main__':
    main()