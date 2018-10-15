from django.shortcuts import render, HttpResponse
from napalm import get_network_driver
from nornir.core import InitNornir
from .forms import ShowForm, DCAccessForm
from .netbox_query import get_device_ip
from .nornir_exec import show_result
from .config_generator import dc_access_template, dc_agg_template
from nornir.plugins.functions.text import print_result
from netmiko import ConnectHandler
import requests, os, json


# Create your views here.


def dashboard(request):
    return render(request, 'dashboard/dashboard.html')


def home(request):
    return render(request, 'home.html')


def show(request):
    if request.method == 'POST':
        form = ShowForm(request.POST)
        if form.is_valid():
            device = request.POST.get('device')
            command = request.POST.get('show_command')
            host_ip = get_device_ip(device)

            result = show_result(device, command)
            return render(request, 'home.html', {'result': result, "device": device, "command": command})
    else:
        form = ShowForm()

    return render(request, 'show.html', {'form': form})


def services(request):
    if request.method == 'POST':
        nr = InitNornir(num_workers=100,
                        inventory="nornir.plugins.inventory.netbox.NBInventory",
                        NBInventory={"nb_url": "http://172.20.22.99",
                                     "nb_token": "49d66235f10e0d388f18e179e756d1d276b898bb"})
        form = DCAccessForm(request.POST)
        if form.is_valid():
            group = request.POST.get('domain')
            tenant = request.POST.get('tenant')
            inventory = nr.inventory.filter(role=group, site="mv1")
            hosts = nr.filter(role=group, site="mv1")
            data_list = []
            if group == "dc-access":
                result = hosts.run(task=dc_access_template, inventory=inventory, tenant=tenant)
                for r in result:
                    data_list.append(result[r][1])
            elif group == "dc-aggregation":
                result = hosts.run(task=dc_agg_template, inventory=inventory, tenant=tenant)
                for r in result:
                    data_list.append(result[r][1])

            return render(request, 'dashboard/dc_access_template.html', {'data': data_list})
    else:
        form = DCAccessForm()

    return render(request, 'dashboard/services_config_list.html', {'form': form})
