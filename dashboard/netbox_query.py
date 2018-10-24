import requests, os, json, ipaddress

NETBOX_API_ROOT = "http://172.20.22.99/api"
NETBOX_DEVICES_ENDPOINT = "/dcim/devices/"
NETBOX_INTERFACES_ENDPOINT = "/dcim/interfaces/"
NETBOX_SITES_ENDPOINT = "/dcim/sites/"
NETBOX_IP_ADDRESSES_ENDPOINT = "/ipam/ip-addresses/"
NETBOX_VLANS_ENDPOINT = "/ipam/vlans/"
NETBOX_PREFIXES_ENDPOINT = "/ipam/prefixes/"
NETBOX_VRFS_ENDPOINT = "/ipam/vrfs/"


class NetboxAPITokenNotFound(Exception):
    pass


def form_headers():
    api_token = '49d66235f10e0d388f18e179e756d1d276b898bb'
    # api_token = os.environ.get("NETBOX_API_TOKEN")
    headers = {
        "Authorization": "Token {}".format(api_token),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    return headers


def get_fex_parents():
    headers = form_headers()
    query_params = {"tenant": "mza-infra", "tag": "fex"}
    r = requests.get(NETBOX_API_ROOT + NETBOX_DEVICES_ENDPOINT,
                     params=query_params, headers=headers)
    nb_devices = r.json()
    parent_switches = []
    for d in nb_devices["results"]:
        parent_switches.append(d["name"])
    return parent_switches


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
    query_params = {"tenant": tenant, "status": 2}

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


def get_prefixes(tenant, tag):
    headers = form_headers()
    query_params = {"tenant": tenant}

    prefixes_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_PREFIXES_ENDPOINT,
        params=query_params, headers=headers
    ).json()
    vrfs_dict = {}
    vrfs = []
    private = []
    public = []
    interfaces = []
    for prefix in prefixes_netbox_dict["results"]:
        r = {}
        if prefix["role"]["slug"] == "inside" or prefix["role"]["slug"] == "dmz":
            r["prefix"] = prefix["prefix"]
            private.append(r)
        elif prefix["role"]["slug"] == "public":
            r["prefix"] = prefix["prefix"]
            public.append(r)
    for prefix in prefixes_netbox_dict["results"]:
        v = {}
        int = {}
        if prefix["vlan"] and prefix["vrf"]:
            int["descr"] = "{} {}".format(tenant, prefix["role"]["slug"])
            int["vlan_id"] = prefix["vlan"]["vid"]
            int["vrf"] = prefix["vrf"]["name"]
            if tag == "agg1":
                int["ip"] = "{}/{}".format(str(ipaddress.ip_network(prefix["prefix"])[2]),
                                           ipaddress.ip_network(prefix["prefix"]).prefixlen)
            elif tag == "agg2":
                int["ip"] = "{}/{}".format(str(ipaddress.ip_network(prefix["prefix"])[3]),
                                           ipaddress.ip_network(prefix["prefix"]).prefixlen)
            int["vip"] = str(ipaddress.ip_network(prefix["prefix"])[1])
            interfaces.append(int)
            #start capture VRFs info
            v["name"] = prefix["vrf"]["name"]
            v["rt"] = prefix["vrf"]["rd"]
            v["role"] = prefix["role"]["slug"]
            if tag == "agg1":
                v["rd"] = prefix["vrf"]["rd"].replace("000", "009")
            elif tag == "agg2":
                v["rd"] = prefix["vrf"]["rd"].replace("000", "010")
            v["descr"] = get_vrf(prefix["vrf"]["name"])["descr"]
            nexthop = str(ipaddress.ip_network(prefix["prefix"])[4])
            v["nexthop"] = nexthop
            if prefix["role"]["slug"] == "outside":
                v["private"] = private
                v["public"] = public
                routes = private + public
                v["routes"] = routes
            else:
                v["routes"] = private

            vrfs.append(v)
    vrfs_dict["vrfs"] = vrfs
    vrfs_dict["interfaces"] = interfaces
    return vrfs_dict
    # return prefixes_netbox_dict["results"]
    # return json.dumps(vlans_netbox_dict, indent=4)


def get_vrf(name):
    headers = form_headers()
    query_params = {"name": name}

    VRFs_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_VRFS_ENDPOINT,
        params=query_params, headers=headers
    ).json()

    result = {}
    for vrf in VRFs_netbox_dict["results"]:
        result["name"] = vrf["name"]
        result["descr"] = vrf["description"]

    return result


def get_vrfs(tenant):
    headers = form_headers()
    query_params = {"tenant": tenant}

    VRFs_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_VRFS_ENDPOINT,
        params=query_params, headers=headers
    ).json()

    result = []
    for vrf in VRFs_netbox_dict["results"]:
        info = {}
        info["name"] = vrf["name"]
        info["rt"] = vrf["rd"]


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
    for d in d["results"]:
        if d.get("primary_ip", {}):
            ip = d["primary_ip"]["address"].split("/")[0]
            return ip


def main():
    #print(get_vrf("VR253000"))
    print(get_prefixes("ipam", "agg1"))


if __name__ == '__main__':
    main()
