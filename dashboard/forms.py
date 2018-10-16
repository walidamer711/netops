from django import forms
import requests, os, json

NETBOX_API_ROOT = "http://172.20.22.99/api"
NETBOX_DEVICES_ENDPOINT = "/dcim/devices/"
NETBOX_TENANTS_ENDPOINT = "/tenancy/tenants/"


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


def get_tenants():
    headers = form_headers()
    query_params = {"group": "meeza-customers"}
    r = requests.get(NETBOX_API_ROOT + NETBOX_TENANTS_ENDPOINT,
                     params=query_params, headers=headers)
    nb_tenants = r.json()
    tenants = []
    for t in nb_tenants["results"]:
        tenant = (t["name"], t["name"])
        tenants.append(tenant)
    return tenants


def form_headers():
    api_token = '49d66235f10e0d388f18e179e756d1d276b898bb'
    # api_token = os.environ.get("NETBOX_API_TOKEN")
    headers = {
        "Authorization": "Token {}".format(api_token),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    return headers


class ShowForm(forms.Form):
    DEVICES = get_devices_list("mza-infra")
    SHOW_COMMANDS = [
        ("show version", "show version"),
        ("show cdp neighbors detail", "show cdp neighbors detail"),
        ("show interface status", "show interface status"),
    ]
    device = forms.CharField(label='Device', widget=forms.Select(choices=get_devices_list("mza-infra")))
    show_command = forms.CharField(label='Command', widget=forms.Select(choices=SHOW_COMMANDS))
    # forms.CharField(label='Device', widget=forms.Select(choices=OPTIONS))
    # forms.MultipleChoiceField(choices=OPTIONS, initial='0', required=True, label='Device')


class DCAccessForm(forms.Form):
    DOMAIN_LIST = [
        ("dc-access", "DC Access"),
        ("dc-aggregation", "DC Aggregation")
    ]
    domain = forms.CharField(label='Select Domain Config', widget=forms.Select(choices=DOMAIN_LIST))
    tenant = forms.CharField(label='Select Customer')
    #tenant = forms.ChoiceField(choices=...)
    def __init__(self, *args, **kwargs):
        super(DCAccessForm, self).__init__(*args, **kwargs)
        self.fields['tenant'].widget = forms.Select(choices=get_tenants())
