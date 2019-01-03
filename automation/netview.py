from nornir import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking
from nornir.core.filter import F
from .helper import start_nornir


def show_result(device, command):
    nr = start_nornir("mza-infra")
    host = nr.filter(name=device)
    result = host.run(task=networking.netmiko_send_command, command_string=command, use_textfsm=True)
    return result[device][0].result

def fex_free_ports(task, command):
    data = {}
    result = []
    r = task.run(task=networking.netmiko_send_command, command_string=command, use_textfsm=True)
    fexs = r.result
    for fex in fexs:
        fex_num = fex['number']
        comm = "show int status fex {}".format(fex_num)
        intfs = task.run(task=networking.netmiko_send_command, command_string=comm, use_textfsm=True)
        down_list = []
        for intf in intfs.result:
            if intf['status'] == 'disabled':
                down_list.append(intf)
        fex['free ports'] = len(down_list)
        result.append(fex)
    data['host'] = task.host.name
    data['result'] = result
    return data


def fex_view_result(command, site):
    if site == "mv1":
        site1 = "mv1"
        site2 = "mv3"
    else:
        site1 = "mv2"
        site2 = "mv2"
    nr = start_nornir('mza-infra')
    hosts = nr.filter(F(has_fex=True) & F(site=site1) | F(has_fex=True) & F(site=site2))
    result = hosts.run(task=fex_free_ports, command=command)
    return result

def main():
   #print_result(net_view_result('show fex'))
    result = fex_view_result('show fex', 'mv2')
    print_result(result)
    for r in result:
        print(result[r][0])




if __name__ == '__main__':
    main()