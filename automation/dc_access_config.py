from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking, text
from automation.helper import start_nornir
from automation.ipam_calls import dc_access_vlans, device_trunks
import yaml

def dc_access_rollback(task, tenant):
    # Generate VLANs group from NetBox
    vlans, vlan_list= dc_access_vlans(tenant, task.host['site'])
    command = "show vlan id {}".format(vlan_list)
    # Get host trunk interfaces
    trunks = device_trunks(f'{task.host.name}', "mza-enc")

    # Transform inventory data to configuration via a template file
    r = task.run(task=text.template_file,
                 name="Rollback Configuration",
                 template="dc_access.j2",
                 path=f"/home/wamer/netops/automation/templates/rollback",
                 vlans=vlans, trunks=trunks)
    # Save the compiled configuration into a host variable
    task.host["config"] = r.result
    # Deploy that configuration to the device using NAPALM
    task.run(task=networking.napalm_configure,
             name="Loading Rollback Configuration on the device",
             replace=False,
             configuration=task.host["config"])


def dc_access_template(task, tenant):
    # Generate VLANs group from NetBox
    vlans = dc_access_vlans(tenant, task.host['site'])
    # Get host trunk interfaces
    trunks = device_trunks(f'{task.host.name}', "mza-enc")

    # Transform inventory data to configuration via a template file
    r = task.run(task=text.template_file,
                 name="Base Configuration",
                 template="dc_access.j2",
                 path=f"/home/wamer/netops/automation/templates/cisco",
                 vlans=vlans, trunks=trunks)


def dc_access_config(task, tenant):
    vlans = dc_access_vlans(tenant, task.host['site'])
    l1 = []
    for v in vlans:
        l1.append(str(v["id"]))
    x = (',').join(l1)
    command = "show vlan id {}".format(x)
    trunks = device_trunks(f'{task.host.name}', "mza-enc")
    r1 = task.run(task=networking.netmiko_send_command, command_string=command)
    if "not found" in r1.result:
        r = task.run(task=text.template_file,
                     name="Base Configuration",
                     template="dc_access.j2",
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
    infra = 'lab'
    tenant = 'ipam'
    site = 'gns3'
    nr = start_nornir(infra)
    h1 = nr.filter(role="dc-access", site=site)
    result = h1.run(task=dc_access_config, tenant=tenant)
    print_result(result)



def config_backup(task):
    c1 = "show vlan id 2536"
    r = task.run(task=networking.napalm_cli, commands=[c1])
    print(r.failed)


if __name__ == '__main__':
    main()