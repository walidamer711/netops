from nornir import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking, text
from automation.ipam_calls import get_outside_vrf, device_trunks, dc_vlans, dc_join_vlans, get_prefixes
from automation.helper import start_nornir

def dc_agg_rollback(task, tenant):
    # Generate VLANs group from NetBox
    vlans = dc_vlans(tenant, task.host['site'])
    # Get host trunk interfaces
    trunks = device_trunks(f'{task.host.name}', "dc-fw")
    # Get VRFs and Interfaces
    vrfs, interfaces = get_prefixes(tenant, f'{task.host["asset_tag"]}')
    # Transform inventory data to configuration via a template file
    r = task.run(task=text.template_file,
                 name="Rollback Configuration",
                 template="dc_agg.j2",
                 path=f"/home/wamer/netops/automation/templates/rollback",
                 vlans=vlans, trunks=trunks, vrfs=vrfs, interfaces=interfaces)

    # Save the compiled configuration into a host variable
    task.host["config"] = r.result

    # Deploy that configuration to the device using NAPALM
    task.run(task=networking.napalm_configure,
             name="Loading Rollback Configuration on the device",
             replace=False,
             configuration=task.host["config"])


def dc_agg_template(task, tenant):
    # Generate VLANs group from NetBox
    vlans = dc_vlans(tenant, task.host['site'])
    # Get host trunk interfaces
    trunks = device_trunks(f'{task.host.name}', "dc-fw")
    # Get VRFs and Interfaces
    vrfs, interfaces = get_prefixes(tenant, f'{task.host["asset_tag"]}')
    print(f'{task.host["asset_tag"]}')
    # Transform inventory data to configuration via a template file
    r = task.run(task=text.template_file,
                 name="Base Configuration",
                 template="dc_agg.j2",
                 path=f"/home/wamer/netops/automation/templates/cisco",
                 cust=tenant, vlans=vlans, trunks=trunks, vrfs=vrfs, interfaces=interfaces)


def dc_agg_config(task, tenant):
    vlans = dc_vlans(tenant, task.host['site'])
    trunks = device_trunks(f'{task.host.name}', "dc-fw")
    vrfs, interfaces = get_prefixes(tenant, f'{task.host["asset_tag"]}')
    vlan_list = dc_join_vlans(tenant)
    command = "show vlan id {}".format(vlan_list)
    r1 = task.run(task=networking.netmiko_send_command, command_string=command)
    if "not found" in r1.result:
        r = task.run(task=text.template_file,
                     name="Base Configuration",
                     template="dc_agg.j2",
                     path=f"/home/wamer/netops/automation/templates/cisco",
                     cust=tenant, vlans=vlans, trunks=trunks, vrfs=vrfs, interfaces=interfaces)

        task.host["config"] = r.result

        task.run(task=networking.napalm_configure,
                 name="Loading Configuration on the device",
                 replace=False,
                 configuration=task.host["config"])
    else:
        print("vlans exist")


def int_agg_config(task, tenant):
    outside_vrf = get_outside_vrf(tenant)
    command = "show vrf {}".format(outside_vrf["name"])
    r1 = task.run(task=networking.netmiko_send_command, command_string=command)
    if "not found" in r1.result:
        print("vrf {} does not exist".format(outside_vrf["name"]))
    else:
        r = task.run(task=text.template_file,
                     name="Outside VRF Configuration",
                     template="int_agg.j2",
                     path=f"/home/wamer/netops/automation/templates/cisco",
                     cust=tenant, vrf=outside_vrf)
        # Save the compiled configuration into a host variable
        task.host["config"] = r.result

        # Deploy that configuration to the device using NAPALM
        task.run(task=networking.napalm_configure,
                 name="Loading Outside VRF Configuration on the device",
                 replace=False,
                 configuration=task.host["config"])


def int_agg_rollback(task, tenant):
    outside_vrf = get_outside_vrf(tenant)

    r = task.run(task=text.template_file,
                 name="Rollback Outside VRF Configuration",
                 template="int_agg.j2",
                 path=f"/home/wamer/netops/automation/templates/rollback",
                 cust=tenant, vrf=outside_vrf)
    # Save the compiled configuration into a host variable
    task.host["config"] = r.result
    # Deploy that configuration to the device using NAPALM
    task.run(task=networking.napalm_configure,
             name="Loading Rollback Outside VRF Configuration on the device",
             replace=False,
             configuration=task.host["config"])


def config_backup(task):
    r = task.run(task=networking.napalm_get, getters=["config"])
    with open(f"backup/{task.host.name}.txt", "w") as f:
        f.write(r.result['config']['running'])


def main():
    infra = 'lab'
    tenant = 'ipam'
    site = 'gns3'

    nr = start_nornir(infra)
    h2 = nr.filter(role="dc-aggregation", site=site)
    #result = h2.run(task=int_agg_config, tenant=tenant)
    result = h2.run(task=show_command)
    print_result(result)


def show_command(task):
    c1 = "show vrf "
    r = task.run(task=networking.netmiko_send_command, command_string="show run vrf VR253000", use_textfsm=True)
    print_result(r)


if __name__ == '__main__':
    main()