from nornir import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking, text
from automation.helper import add_account, dc_access_vlans, device_trunks


def dc_access_template(task, tenant):
    # Generate VLANs group from NetBox
    vlans, vlan_list= dc_access_vlans(tenant, task.host['site'])
    command = "show vlan id {}".format(vlan_list)
    # Get host trunk interfaces
    trunks = device_trunks(f'{task.host.name}', "mza-enc")
    # Transform inventory data to configuration via a template file
    r = task.run(task=text.template_file,
                 name="Base Configuration",
                 template="access.j2",
                 path=f"/home/wamer/netops/automation/templates/cisco",
                 vlans=vlans, trunks=trunks)


def dc_access_config(task, tenant):
    # Generate VLANs group from NetBox
    vlans, vlan_list= dc_access_vlans(tenant, task.host['site'])
    command = "show vlan id {}".format(vlan_list)
    # Get host trunk interfaces
    trunks = device_trunks(f'{task.host.name}', "mza-enc")
    r1 = task.run(task=networking.netmiko_send_command, command_string=command)
    if "not found" in r1.result:
        # Transform inventory data to configuration via a template file
        r = task.run(task=text.template_file,
                     name="Base Configuration",
                     template="access.j2",
                     path=f"/home/wamer/netops/automation/templates/cisco",
                     vlans=vlans, trunks=trunks)

        # Save the compiled configuration into a host variable
        task.host["config"] = r.result

        # Deploy that configuration to the device using NAPALM
        task.run(task=networking.napalm_configure,
                 name="Loading Configuration on the device",
                 replace=False,
                 configuration=task.host["config"])
    else:
        print("vlans exist")



def main():
    print(dc_access_vlans("ipam", "gns3"))
    nr = InitNornir(core={"num_workers": 100},
               inventory={"plugin": "nornir.plugins.inventory.netbox.NBInventory",
                          "options": {"nb_url": "http://172.20.22.99",
                                      "nb_token": "49d66235f10e0d388f18e179e756d1d276b898bb"}})
    inventory = nr.inventory.filter(role="dc-access", site="gns3")
    add_account(inventory)
    hosts = nr.filter(role="dc-access", site="gns3")
    #result = hosts.run(task=config_backup)
    result = hosts.run(task=dc_access_template, tenant="ipam")
    print_result(result)
    #for r in result:
    #    print(dir(result[r][1]))
    #    print(result[r][2].changed)

    #print(get_dc_vlans("qlc", "mv2"))


def config_backup(task):
    c1 = "show vlan id 2536"
    r = task.run(task=networking.napalm_cli, commands=[c1])
    print(r.failed)


if __name__ == '__main__':
    main()