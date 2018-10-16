from nornir.core import InitNornir
from nornir.plugins.functions.text import print_result, print_title
from nornir.plugins.tasks import networking, text
from napalm import get_network_driver
from .netbox_query import get_device_trunks, get_dc_vlans


def netbox_inventory():
    InitNornir(num_workers=100,
               inventory="nornir.plugins.inventory.netbox.NBInventory",
               NBInventory={"nb_url": "http://172.20.22.99",
                            "nb_token": "49d66235f10e0d388f18e179e756d1d276b898bb"})


def access_config(task):
    print(f"hi! My name is {task.host.name} and I live in {task.host['platform']}")
    # Transform inventory data to configuration via a template file
    r = task.run(task=text.template_file,
                 name="Base Configuration",
                 template="access.j2",
                 path=f"/home/wamer/netops/dashboard/templates/cisco")

    # Save the compiled configuration into a host variable
    task.host["config"] = r.result

    driver = get_network_driver(f"{task.host['platform']}")

    with driver(task.host["hostname"], task.host["username"], task.host["password"],
                optional_args={"transport": "http"}) as device:
        print(device.cli(["show vlan id 922"]))


def dc_access_template(task, inventory, tenant):
    # Generate VLANs group from NetBox
    vlans_group = get_dc_vlans(tenant, "dc-access").pop("dc-access")
    inventory.hosts[f'{task.host.name}'].data.update(vlans_group)
    # Get host trunk interfaces
    device_trunks = get_device_trunks(f'{task.host.name}', "mza-enc")
    if device_trunks:
        inventory.hosts[f'{task.host.name}'].data.update(device_trunks)
    # Transform inventory data to configuration via a template file
    r = task.run(task=text.template_file,
                 name="Base Configuration",
                 template="access.j2",
                 path=f"/home/wamer/netops/dashboard/templates/cisco")

    ## Save the compiled configuration into a host variable
    task.host["config"] = r.result


def dc_agg_template(task, inventory, tenant):
    # Generate VLANs group from NetBox
    vlans_group = get_dc_vlans(tenant, "dc-aggregation").pop("dc-aggregation")
    inventory.hosts[f'{task.host.name}'].data.update(vlans_group)
    # Get host trunk interfaces
    device_trunks = get_device_trunks(f'{task.host.name}', "dc-fw")
    if device_trunks:
        inventory.hosts[f'{task.host.name}'].data.update(device_trunks)
    # Transform inventory data to configuration via a template file
    r = task.run(task=text.template_file,
                 name="Base Configuration",
                 template="agg.j2",
                 path=f"/home/wamer/netops/dashboard/templates/cisco")

    # Save the compiled configuration into a host variable
    task.host["config"] = r.result


def main():
    nr = InitNornir(num_workers=100,
                    inventory="nornir.plugins.inventory.netbox.NBInventory",
                    NBInventory={"nb_url": "http://172.20.22.99",
                                 "nb_token": "49d66235f10e0d388f18e179e756d1d276b898bb"})
    inventory = nr.inventory.filter(role="dc-access", site="mv1")
    dc_access_hosts = nr.filter(role="dc-access", site="mv1")
    result = dc_access_hosts.run(task=dc_access_template, inventory=inventory, tenant="ipam")
    #inventory = nr.inventory.filter(role="dc-aggregation", site="mv1")
    #dc_agg_hosts = nr.filter(role="dc-aggregation", site="mv1")
    #result = dc_agg_hosts.run(task=dc_agg_template, inventory=inventory)
    print_result(result)
    #for r in result:
    #    print(r)
    #    print(type(result[r][1]))

def test_netmike(task):
    task.run(task=networking.netmiko_send_command, command_string="show version", use_textfsm=True)


if __name__ == '__main__':
    main()
