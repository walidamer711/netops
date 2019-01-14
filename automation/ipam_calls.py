import requests, ipaddress



NETBOX_API_ROOT = "http://172.20.22.99/api"
NETBOX_DEVICES_ENDPOINT = "/dcim/devices/"
NETBOX_INTERFACES_ENDPOINT = "/dcim/interfaces/"
NETBOX_SITES_ENDPOINT = "/dcim/sites/"
NETBOX_IP_ADDRESSES_ENDPOINT = "/ipam/ip-addresses/"
NETBOX_VLANS_ENDPOINT = "/ipam/vlans/"
NETBOX_PREFIXES_ENDPOINT = "/ipam/prefixes/"
NETBOX_VRFS_ENDPOINT = "/ipam/vrfs/"


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
    return vlans


def dc_vlans(tenant, site):
    headers = form_headers()
    query_params = {"tenant": tenant, "site": site, "status": 2}

    vlans_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_VLANS_ENDPOINT,
        params=query_params, headers=headers
    ).json()
    vlans = []
    for v in vlans_netbox_dict["results"]:
        if v["role"]["slug"] == "inside" or \
                v["role"]["slug"] == "dmz" or \
                v["role"]["slug"] == "outside" or \
                v["role"]["slug"] == "wan":
            temp = {}
            temp["name"] = v["name"]
            temp["id"] = v["vid"]
            temp["role"] = v["role"]["slug"]
            vlans.append(temp)
    return vlans


def dc_join_vlans(tenant):
    headers = form_headers()
    query_params = {"tenant": tenant}

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
        if prefix["role"]["slug"] == "outside" or prefix["role"]["slug"] == "wan":
            int = {}
            int["nameif"] = "{}".format(prefix["role"]["slug"])
            int["role"] = "{}".format(prefix["role"]["slug"])
            int["vlan_id"] = prefix["vlan"]["vid"]
            int["ip"] = "{}".format(str(ipaddress.ip_network(prefix["prefix"])[4]))
            int["network"] = "{}".format(str(ipaddress.ip_network(prefix["prefix"]).network_address))
            int["mask"] = "{}".format(str(ipaddress.ip_network(prefix["prefix"]).netmask))
            int["vip"] = str(ipaddress.ip_network(prefix["prefix"])[1])
            interfaces.append(int)
        elif prefix["role"]["slug"] == "inside" or prefix["role"]["slug"] == "dmz":
            int = {}
            int["nameif"] = "{}".format(prefix["role"]["slug"])
            int["role"] = "{}".format(prefix["role"]["slug"])
            int["vlan_id"] = prefix["vlan"]["vid"]
            int["ip"] = "{}".format(str(ipaddress.ip_network(prefix["prefix"])[1]))
            int["network"] = "{}".format(str(ipaddress.ip_network(prefix["prefix"]).network_address))
            int["mask"] = "{}".format(str(ipaddress.ip_network(prefix["prefix"]).netmask))
            int["vip"] = str(ipaddress.ip_network(prefix["prefix"])[1])
            interfaces.append(int)

    return interfaces


def get_pat_ip(tenant):
    headers = form_headers()
    query_params = {"tenant": tenant}

    pub_addr_netbox = requests.get(
        NETBOX_API_ROOT + NETBOX_IP_ADDRESSES_ENDPOINT,
        params=query_params, headers=headers
    ).json()

    pat_ip = []
    for addr in pub_addr_netbox["results"]:
        pat_ip.append(str(ipaddress.ip_network(addr["address"]).network_address))

    return pat_ip[0]


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


def get_wan_vrf(tenant, tag):
    headers = form_headers()
    query_params = {"tenant": tenant}

    VRFs_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_VRFS_ENDPOINT,
        params=query_params, headers=headers
    ).json()
    v = {}
    for vrf in VRFs_netbox_dict['results']:
        if vrf['custom_fields']['vrfrole'] and vrf['custom_fields']['vrfrole']['label'] == 'wan':
            v["name"] = vrf["name"]
            v["rt"] = vrf["rd"]
            v["role"] = "wan"
            v["descr"] = vrf["description"]
            if "wan1" in tag:
                v["rd"] = "{}005".format(vrf["rd"][:-3])
            elif"wan2" in tag:
                v["rd"] = "{}006".format(vrf["rd"][:-3])

    return v


def get_outside_vrf(tenant):
    headers = form_headers()
    query_params = {"tenant": tenant}

    VRFs_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_VRFS_ENDPOINT,
        params=query_params, headers=headers
    ).json()

    prefixes_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_PREFIXES_ENDPOINT,
        params=query_params, headers=headers
    ).json()

    pub_addr_netbox = requests.get(
        NETBOX_API_ROOT + NETBOX_IP_ADDRESSES_ENDPOINT,
        params=query_params, headers=headers
    ).json()

    v = {}
    public = []

    for vrf in VRFs_netbox_dict['results']:
        if vrf['custom_fields']['vrfrole'] and vrf['custom_fields']['vrfrole']['label'] == 'outside':
            v["name"] = vrf["name"]
            v["role"] = "outside"

    for prefix in prefixes_netbox_dict["results"]:
        if prefix["role"]["slug"] == "public":
            public.append(prefix["prefix"])

    for addr in pub_addr_netbox["results"]:
        public.append(addr["address"])

    v["public"] = public

    return v


def get_prefixes(tenant, tag):
    headers = form_headers()
    query_params = {"tenant": tenant}

    prefixes_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_PREFIXES_ENDPOINT,
        params=query_params, headers=headers
    ).json()

    pub_addr_netbox = requests.get(
        NETBOX_API_ROOT + NETBOX_IP_ADDRESSES_ENDPOINT,
        params=query_params, headers=headers
    ).json()
    vrfs_query = get_vrfs(tenant)
    vrfs_dict = {}
    vrfs = []
    private = []
    public = []
    interfaces = []
    routes = []
    for prefix in prefixes_netbox_dict["results"]:
        #role must be defined for each prefix under this tenant
        if prefix["role"]["slug"] == "inside" or prefix["role"]["slug"] == "dmz":
            private.append(prefix["prefix"])
            routes.append(prefix["prefix"])
        elif prefix["role"]["slug"] == "public":
            public.append(prefix["prefix"])
            routes.append(prefix["prefix"])

    for addr in pub_addr_netbox["results"]:
        routes.append(addr["address"])

    for prefix in prefixes_netbox_dict["results"]:

        v = {}
        int = {}
        if prefix["role"]["slug"] == "outside" or prefix["role"]["slug"] == "wan":
            int["descr"] = "{} {}".format(tenant, prefix["role"]["slug"])
            int["vlan_id"] = prefix["vlan"]["vid"]
            if prefix["role"]["slug"] == "outside":
                int["vrf"] = "outside"
            elif prefix["role"]["slug"] == "wan":
                int["vrf"] = "wan"
            if "agg1" in tag:
                int["ip"] = "{}/{}".format(str(ipaddress.ip_network(prefix["prefix"])[2]),
                                           ipaddress.ip_network(prefix["prefix"]).prefixlen)
            elif "agg2" in tag:
                int["ip"] = "{}/{}".format(str(ipaddress.ip_network(prefix["prefix"])[3]),
                                           ipaddress.ip_network(prefix["prefix"]).prefixlen)
            int["vip"] = str(ipaddress.ip_network(prefix["prefix"])[1])
            int["tag"] = tag
            interfaces.append(int)
            #start capture VRFs info
            vrf = vrfs_query[prefix["role"]["slug"]]
            v["name"] = vrf['name']
            v["rt"] = vrf['rd']
            v["role"] = vrf["role"]
            if "agg1" in tag:
                v["rd"] = "{}009".format(vrf["rd"][:-3])
            elif"agg2" in tag:
                v["rd"] = "{}010".format(vrf["rd"][:-3])
            v["descr"] = vrf['descr']
            nexthop = str(ipaddress.ip_network(prefix["prefix"])[4])
            v["nexthop"] = nexthop
            if prefix["role"]["slug"] == "outside":
                v["routes"] = routes
            else:
                v["routes"] = private

            vrfs.append(v)
    vrfs_dict["vrfs"] = vrfs
    vrfs_dict["interfaces"] = interfaces
    return vrfs, interfaces


def get_vrfs(tenant):
    headers = form_headers()
    query_params = {'tenant': tenant}

    VRFs_netbox_dict = requests.get(
        NETBOX_API_ROOT + NETBOX_VRFS_ENDPOINT,
        params=query_params, headers=headers
    ).json()
    vrfs = {}

    for vrf in VRFs_netbox_dict['results']:
        v = {}
        v["name"] = vrf["name"]
        v["rd"] = vrf["rd"]
        v["descr"] = vrf["description"]
        v["role"] = vrf['custom_fields']['vrfrole']['label']
        vrfs[vrf['custom_fields']['vrfrole']['label']] = v

    return vrfs


def main():
    #print(get_prefixes("ipam", "agg1"))
    print(get_outside_vrf("ipam"))
    print(get_wan_vrf("ipam", "wan1"))
    #print(get_vrfs("ipam"))

if __name__ == '__main__':
    main()