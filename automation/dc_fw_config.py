from netmiko import ConnectHandler
from nornir import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking, text
from automation.helper import add_account, device_trunks, dc_fw_prefixes


def dc_fw_config(task, tenant):
    trunks = device_trunks(f'{task.host.name}', "agg")
    interafces = dc_fw_prefixes(tenant)
    # Transform inventory data to configuration via a template file
    r = task.run(task=text.template_file,
                 name="Base Configuration",
                 template="dc_fw.j2",
                 path=f"/home/wamer/netops/automation/templates/cisco",
                 interfaces=interafces, trunk=trunks[0])

    task.host["config"] = r.result

    task.run(task=networking.netmiko_send_config,
             name="Loading Configuration on the device",
             config_commands=task.host["config"])



def main():
    nr = InitNornir(core={"num_workers": 100},
                    inventory={"plugin": "nornir.plugins.inventory.netbox.NBInventory",
                               "options": {"nb_url": "http://172.20.22.99",
                                           "nb_token": "49d66235f10e0d388f18e179e756d1d276b898bb"}})
    inventory = nr.inventory.filter(role="dc-fw", site="gns3")
    add_account(inventory)
    hosts = nr.filter(role="dc-fw", site="gns3")
    result = hosts.run(task=dc_fw_config, tenant="ipam")
    print_result(result)


cisco_asa = {
  'device_type': 'cisco_asa',
  'ip': '172.20.22.41',
  'username': 'wamer',
  'password': 'Weda711;',
  'secret': 'Weda711;',
}


def conn_netmiko():
    with ConnectHandler(**cisco_asa) as conn:
        conn.send_command('changeto system')
        config_output = conn.send_command('show running')
        print(config_output)



if __name__ == '__main__':
    main()