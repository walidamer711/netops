import requests, os, json

NETBOX_API_ROOT = "http://172.20.22.99/api"
NETBOX_DEVICES_ENDPOINT = "/dcim/devices/"
NETBOX_INTERFACES_ENDPOINT = "/dcim/interfaces/"
NETBOX_SITES_ENDPOINT = "/dcim/sites/"
NETBOX_IP_ADDRESSES_ENDPOINT = "/ipam/ip-addresses/"
NETBOX_VLANS_ENDPOINT = "/ipam/vlans/"
NETBOX_PREFIXES_ENDPOINT = "/ipam/prefixes/"


class NetboxAPITokenNotFound(Exception):
    pass


def get_hosts(tenant):
    headers = form_headers()
    query_params = {"tenant": tenant}
    r = requests.get(NETBOX_API_ROOT + NETBOX_DEVICES_ENDPOINT,
                     params=query_params, headers=headers)
    nb_devices = r.json()
    devices = {}
    for d in nb_devices["results"]:

        # Create temporary dict
        temp = {}

        # Add value for IP address
        if d.get("primary_ip", {}):
            temp["hostname"] = d["primary_ip"]["address"].split("/")[0]

        # Add values that don't have an option for 'slug'
        temp["serial"] = d["serial"]
        temp["vendor"] = d["device_type"]["manufacturer"]["name"]
        temp["asset_tag"] = d["asset_tag"]

        # Add values that do have an option for 'slug'

        temp["site"] = d["site"]["slug"]
        temp["role"] = d["device_role"]["slug"]
        temp["model"] = d["device_type"]["slug"]
        # Attempt to add 'platform' based of value in 'slug'
        temp["platform"] = d["platform"]["slug"] if d["platform"] else None
        temp["groups"] = [d["device_role"]["slug"]]
        temp["trunks"] = get_device_trunks(d["name"])
        # Assign temporary dict to outer dict
        devices[d["name"]] = temp
    return devices


def get_device_trunks(device, interface_tag):
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
    t_dict["trunks"] = tl
    return t_dict


def get_dc_vlans(tenant, group):
    headers = form_headers()
    query_params = {"tenant": tenant}

    vlans_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_VLANS_ENDPOINT,
        params=query_params, headers=headers
    ).json()
    d = {}
    f = {}
    access_vlans = []
    agg_vlans = []
    for v in vlans_netbox_dict["results"]:
        if v["role"]["slug"] == "inside" or v["role"]["slug"] == "dmz":
            # Create temporary dict
            temp = {}
            temp["name"] = v["name"]
            temp["id"] = v["vid"]
            temp["role"] = v["role"]["slug"]
            access_vlans.append(temp)
            agg_vlans.append(temp)
        else:
            temp = {}
            temp["name"] = v["name"]
            temp["id"] = v["vid"]
            temp["role"] = v["role"]["slug"]
            agg_vlans.append(temp)
    if group == "dc-access":
        d["vlans"] = access_vlans
        f[group] = d
        return f
    elif group == "dc-aggregation":
        d["vlans"] = agg_vlans
        f[group] = d
        return f
    else:
        return None
    # return json.dumps(vlans_netbox_dict, indent=4)


def get_prefixes(tenant):
    headers = form_headers()
    query_params = {"tenant": tenant}

    prefixes_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_PREFIXES_ENDPOINT,
        params=query_params, headers=headers
    ).json()

    result = []
    for prefix in prefixes_netbox_dict["results"]:
        # if prefix["status"]["label"] == "Reserved":
        info = {}
        if prefix["vlan"]:
            info["vlan_name"] = prefix["vlan"]["name"]
            # info["status"] = prefix["status"]["label"]
            info["vlan_id"] = prefix["vlan"]["vid"]
            info["prefix"] = prefix["prefix"]
            info["role"] = prefix["role"]["slug"]
            result.append(info)

    return result
    # return prefixes_netbox_dict["results"]
    # return json.dumps(vlans_netbox_dict, indent=4)


def get_devices_list(tenant):
    headers = form_headers()
    query_params = {"tenant": tenant}
    r = requests.get(NETBOX_API_ROOT + NETBOX_DEVICES_ENDPOINT,
                     params=query_params, headers=headers)
    nb_devices = r.json()
    devices = []
    for d in nb_devices["results"]:
        device = (d["name"], d["name"])
        devices.append(device)
    return devices


def get_device_ip(hostname):
    headers = form_headers()
    query_params = {"name": hostname}
    r = requests.get(NETBOX_API_ROOT + NETBOX_DEVICES_ENDPOINT,
                     params=query_params, headers=headers)
    d = r.json()
    print(d["results"])
    for d in d["results"]:
        if d.get("primary_ip", {}):
            ip = d["primary_ip"]["address"].split("/")[0]
            return ip


def form_headers():
    api_token = '49d66235f10e0d388f18e179e756d1d276b898bb'
    # api_token = os.environ.get("NETBOX_API_TOKEN")
    headers = {
        "Authorization": "Token {}".format(api_token),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    return headers


def main():
    print(get_device_ip("MV1_N5K_DC_ACC_01"))


if __name__ == '__main__':
    main()
