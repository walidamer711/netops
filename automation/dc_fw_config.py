
from netmiko import ConnectHandler
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking, text
from decouple import config
from automation.helper import start_nornir
from automation.ipam_calls import device_trunks, dc_fw_prefixes, get_pat_ip



def dc_fw_rollback(task, tenant):
    trunks = device_trunks(f'{task.host.name}', "agg")
    interafces = dc_fw_prefixes(tenant)
    # Transform inventory data to configuration via a template file
    r = task.run(task=text.template_file,
                 name="Rollback Configuration",
                 template="dc_fw.j2",
                 path=f"/home/wamer/netops/automation/templates/rollback",
                 interfaces=interafces, trunk=trunks[0])

    task.host["config"] = r.result

    task.run(task=networking.netmiko_send_config,
             name="Loading Rollback Configuration on the device",
             config_commands=task.host["config"])


def sys_fw_config(task, tenant):
    #trunks = device_trunks(f'{task.host.name}', "agg")
    interfaces = dc_fw_prefixes(tenant)
    intf_status =False
    for intf in interfaces:
        r = task.run(task=networking.netmiko_send_command,
                 name="Loading Configuration on the device",
                 command_string="changeto system\n show interface Port-channel11.{}".format(intf["vlan_id"]))
        if "ERROR" not in r.result:
            intf_status = True
            break
    print(intf_status)
    # Transform inventory data to configuration via a template file
    r = task.run(task=text.template_file,
                 name="Base Configuration",
                 template="sys_fw.j2",
                 path=f"/home/wamer/netops/automation/templates/cisco",
                 interfaces=interfaces, cust=tenant)

    task.host["config"] = r.result

    task.run(task=networking.netmiko_send_config,
             name="Loading Configuration on the device",
             config_commands=task.host["config"])
    #task.run(task=networking.netmiko_send_command,
    #         name="Loading Configuration on the device",
    #         command_string="changeto system\n show interface Port-channel11.2536\n show interface Port-channel11.2537")


def dc_fw_config(task, tenant):
    trunks = device_trunks(f'{task.host.name}', "agg")
    interfaces = dc_fw_prefixes(tenant)
    pat_ip = get_pat_ip(tenant)
    r = task.run(task=text.template_file,
                 name="Base Configuration",
                 template="dc_fw.j2",
                 path=f"/home/wamer/netops/automation/templates/cisco",
                 interfaces=interfaces, trunk=trunks[0], cust=tenant,
                 site=task.host['site'], pat_ip=pat_ip)

    task.host["config"] = r.result

    task.run(task=networking.netmiko_send_config,
             name="Loading Configuration on the device",
             config_commands=task.host["config"])



def main():
    infra = 'lab'
    tenant = 'ipam'
    site = 'gns3'

    nr = start_nornir(infra)
    h3 = nr.filter(role="dc-fw", site=site)
    result = h3.run(task=dc_fw_config, tenant=tenant)
    print_result(result)







def conn_netmiko():
    with ConnectHandler(**cisco_asa) as conn:
        conn.send_command('changeto system')
        config_output = conn.send_command('show running')
        print(config_output)



if __name__ == '__main__':
    main()