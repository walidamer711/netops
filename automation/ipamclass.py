import requests, ipaddress
from pprint import pprint

class TenantVars(object):

    def __init__(self,
                 tenant=None, site=None):
        self.NETBOX_API_ROOT = "http://172.20.22.99/api"
        self.NETBOX_DEVICES_ENDPOINT = "/dcim/devices/"
        self.NETBOX_INTERFACES_ENDPOINT = "/dcim/interfaces/"
        self.NETBOX_SITES_ENDPOINT = "/dcim/sites/"
        self.NETBOX_IP_ADDRESSES_ENDPOINT = "/ipam/ip-addresses/"
        self.NETBOX_VLANS_ENDPOINT = "/ipam/vlans/"
        self.NETBOX_PREFIXES_ENDPOINT = "/ipam/prefixes/"
        self.NETBOX_VRFS_ENDPOINT = "/ipam/vrfs/"
        self.API_TOKEN = '49d66235f10e0d388f18e179e756d1d276b898bb'
        self.tenant = tenant
        self.site = site
        self.data = {}

        self.get_vlans()
        self.get_vrfs()


    def form_headers(self):
        # api_token = os.environ.get("NETBOX_API_TOKEN")
        headers = {
            "Authorization": "Token {}".format(self.API_TOKEN),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        return headers


    def get_vlans(self, **kwargs):
        headers = self.form_headers()
        query_params = {"tenant": self.tenant, "site": self.site}
        query_params.update(kwargs.get("query_params", {}))
        nb_vlans = requests.get(
            self.NETBOX_API_ROOT + self.NETBOX_VLANS_ENDPOINT,
            params=query_params, headers=headers
        ).json()
        vlans = []
        for v in nb_vlans["results"]:
            temp = {}
            temp["name"] = v["name"]
            temp["id"] = v["vid"]
            temp["role"] = v["role"]["slug"] if v["role"] else None
            vlans.append(temp)
        self.data['vlans'] = vlans
        return vlans

    def get_vrfs(self):
        headers = self.form_headers()
        query_params = {'tenant': self.tenant}

        VRFs_netbox_dict = requests.get(
            self.NETBOX_API_ROOT + self.NETBOX_VRFS_ENDPOINT,
            params=query_params, headers=headers
        ).json()
        vrfs = {}

        for vrf in VRFs_netbox_dict['results']:
            v = {}
            v["name"] = vrf["name"]
            v["rd"] = vrf["rd"]
            v["descr"] = vrf["description"]
            v["role"] = vrf['custom_fields']['vrfrole']['label'] if vrf['custom_fields']['vrfrole'] else None
            vrfs[vrf['custom_fields']['vrfrole']['label']] = v
        self.data['vrfs'] = vrfs
        return vrfs


def main():
    i = TenantVars('commvault', 'mv1')
    pprint(i.data)
    query_params = {'group': 'dc-svc', 'role': 'mgmt'}
    print(i.get_vlans(query_params=query_params))
    #print(i.get_vrfs('acta'))

if __name__ == '__main__':
    main()