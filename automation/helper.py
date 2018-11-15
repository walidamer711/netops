from decouple import config
import requests, ipaddress

LAB_ACCOUNT = {"username": 'admin', "password": 'admin', "secret": "admin"}
ACCOUNT = {"username": config('username'), "password": config('password')}

NETBOX_API_ROOT = "http://172.20.22.99/api"
NETBOX_DEVICES_ENDPOINT = "/dcim/devices/"
NETBOX_INTERFACES_ENDPOINT = "/dcim/interfaces/"
NETBOX_SITES_ENDPOINT = "/dcim/sites/"
NETBOX_IP_ADDRESSES_ENDPOINT = "/ipam/ip-addresses/"
NETBOX_VLANS_ENDPOINT = "/ipam/vlans/"
NETBOX_PREFIXES_ENDPOINT = "/ipam/prefixes/"
NETBOX_VRFS_ENDPOINT = "/ipam/vrfs/"


def add_account_lab(inventory):
    for h in inventory.hosts:
        inventory.hosts[h].username = LAB_ACCOUNT['username']
        inventory.hosts[h].password = LAB_ACCOUNT['password']


def add_account(inventory):
    for h in inventory.hosts:
        inventory.hosts[h].username = ACCOUNT['username']
        inventory.hosts[h].password = ACCOUNT['password']


def form_headers():
    api_token = '49d66235f10e0d388f18e179e756d1d276b898bb'
    # api_token = os.environ.get("NETBOX_API_TOKEN")
    headers = {
        "Authorization": "Token {}".format(api_token),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    return headers


def dc_access_vlans(tenant, site):
    headers = form_headers()
    query_params = {"tenant": tenant, "site": site, "status": 2}

    vlans_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_VLANS_ENDPOINT,
        params=query_params, headers=headers
    ).json()
    l1 = []
    vlans = []
    for v in vlans_netbox_dict["results"]:
        if v["role"]["slug"] == "inside" or v["role"]["slug"] == "dmz":
            # Create temporary dict
            temp = {}
            temp["name"] = v["name"]
            temp["id"] = v["vid"]
            l1.append(str(v["vid"]))
            temp["role"] = v["role"]["slug"]
            vlans.append(temp)
    x = (',').join(l1)
    return vlans, x


def dc_vlans(tenant, site):
    headers = form_headers()
    query_params = {"tenant": tenant, "site": site, "status": 2}

    vlans_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_VLANS_ENDPOINT,
        params=query_params, headers=headers
    ).json()
    vlans = []
    for v in vlans_netbox_dict["results"]:
        # Create temporary dict
        temp = {}
        temp["name"] = v["name"]
        temp["id"] = v["vid"]
        temp["role"] = v["role"]["slug"]
        vlans.append(temp)
    return vlans


def dc_join_vlans(tenant):
    headers = form_headers()
    query_params = {"tenant": tenant, "status": 2}

    vlans_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_VLANS_ENDPOINT,
        params=query_params, headers=headers
    ).json()
    l1 = []
    for v in vlans_netbox_dict["results"]:
        l1.append(str(v["vid"]))
    x = (',').join(l1)
    return x


def device_trunks(device, interface_tag):
    """
    :param device: device name in NetBox
    :param interface_tag: tag of the interface in NetBox
    :return: list of trunk interfaces
    """
    headers = form_headers()
    query_params = {"device": device, "tag": interface_tag}
    trunks = requests.get(
        NETBOX_API_ROOT + NETBOX_INTERFACES_ENDPOINT,
        params=query_params, headers=headers
    ).json()
    tl = []
    t_dict = {}
    for i in trunks["results"]:
        tl.append(i["name"])
    # t_dict["trunks"] = tl
    return tl


def dc_fw_prefixes(tenant):
    headers = form_headers()
    query_params = {"tenant": tenant}

    prefixes_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_PREFIXES_ENDPOINT,
        params=query_params, headers=headers
    ).json()
    interfaces = []
    for prefix in prefixes_netbox_dict["results"]:
        if prefix["vlan"]:
            int = {}
            int["nameif"] = "{}".format(prefix["role"]["slug"])
            int["role"] = "{}".format(prefix["role"]["slug"])
            int["vlan_id"] = prefix["vlan"]["vid"]
            int["ip"] = "{}".format(str(ipaddress.ip_network(prefix["prefix"])[4]))
            int["mask"] = "{}".format(str(ipaddress.ip_network(prefix["prefix"]).netmask))
            int["vip"] = str(ipaddress.ip_network(prefix["prefix"])[1])
            interfaces.append(int)
    return interfaces
