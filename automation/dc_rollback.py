from nornir import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking, text
from decouple import config
from nornir.core.inventory import ConnectionOptions
from automation.ipam_calls import dc_access_vlans,device_trunks, dc_vlans, dc_fw_prefixes, get_prefixes, get_outside_vrf
from automation.helper import start_nornir


def dc_access_rollback(task, tenant):
    # Generate VLANs group from NetBox
    vlans, vlan_list = dc_access_vlans(tenant, task.host['site'])
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

def main():
    nr = start_nornir()

    h1 = nr.filter(role="dc-access", site="gns3")
    r1 = h1.run(task=dc_access_rollback, tenant="ipam")
    print_result(r1)
    h2 = nr.filter(role="dc-aggregation", site="gns3")
    r21 = h2.run(task=int_agg_rollback, tenant="ipam")
    print_result(r21)
    r22 = h2.run(task=dc_agg_rollback, tenant="ipam")
    print_result(r22)
    h3 = nr.filter(role="dc-fw", site="gns3")
    r3 = h3.run(task=dc_fw_rollback, tenant="ipam")
    print_result(r3)


if __name__ == '__main__':
    main()