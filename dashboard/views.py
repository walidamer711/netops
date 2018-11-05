from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from nornir.core import InitNornir
from nornir.plugins.tasks import networking, text
from .forms import ShowForm, DCAccessForm, VLANCheck, FEXForm
from .netbox_query import get_device_ip
from .nornir_exec import show_result
from .config_generator import dc_access_template, dc_agg_template
from .netview import fex_view_result
from .checkview import check_dc_vlan
from nornir.plugins.functions.text import print_result


# Create your views here.

@login_required
def dashboard(request):
    return render(request, 'dashboard/dashboard.html')

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def show(request):
    if request.method == 'POST':
        form = ShowForm(request.POST)
        if form.is_valid():
            device = request.POST.get('device')
            command = request.POST.get('show_command')
            host_ip = get_device_ip(device)

            result = show_result(device, command)
            return render(request, 'dashboard/show_result.html', {'result': result, "device": device, "command": command})
    else:
        form = ShowForm()

    return render(request, 'dashboard/show.html', {'form': form})


@login_required
def checks_view(request, check):
    data_list = []
    if check == 'vlan':
        if request.method == 'POST':
            form = VLANCheck(request.POST)
            if form.is_valid():
                tenant = request.POST.get('tenant')
                site = request.POST.get('site')
                result = check_dc_vlan(tenant, site)
                for r in result:
                    data_list.append(result[r][0])
                return render(request, 'dashboard/check_vlan_view.html', {'data': data_list})
        else:
            form = VLANCheck()

    return render(request, 'dashboard/check_vlan_view.html', {'form': form})



@login_required
def network_views(request, view):
    data_list = []
    if view == 'fex':
        if request.method == 'POST':
            form = FEXForm(request.POST)
            if form.is_valid():
                site = request.POST.get('site')
                command = "show fex"
                result = fex_view_result(command, site)
                for r in result:
                    data_list.append(result[r][0])
                return render(request, 'dashboard/show_result.html', {'data': data_list})
        else:
            form = FEXForm()

    return render(request, 'dashboard/show_result.html', {'form': form})


@login_required
def services(request):
    if request.method == 'POST':
        nr = InitNornir(config_file="/home/wamer/netops/dashboard/config.yaml")
        form = DCAccessForm(request.POST)
        if form.is_valid():
            group = request.POST.get('domain')
            tenant = request.POST.get('tenant')
            site = request.POST.get('site')
            inventory = nr.inventory.filter(role=group, site=site)
            hosts = nr.filter(role=group, site=site)
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
