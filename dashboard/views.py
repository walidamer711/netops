from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from nornir import InitNornir
from .forms import ShowForm, DCAccessForm, VLANCheck, FEXForm, QOSForm
from automation.dc_debug import dc_agg_template, dc_access_template
from automation.netview import fex_view_result
from automation.checkview import check_dc_vlan
from automation.int_qos import qos_view_result
from automation.helper import start_nornir
from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

# Create your views here.

@login_required
def dashboard(request):
    return render(request, 'dashboard/dashboard.html')

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def show(request):

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
    free_ports = {'MV2_N5K_DC_ACC_01': {'101': 35}}
    if view == 'fex':
        if request.method == 'POST':
            form = FEXForm(request.POST)
            if form.is_valid():
                site = request.POST.get('site')
                command = "show fex"
                result = fex_view_result(command, site)
                for r in result:
                    data_list.append(result[r][0].result)
                return render(request, 'dashboard/show_result.html', {'data': data_list})
        else:
            form = FEXForm()
    elif view == 'qos':
        if request.method == 'POST':
            form = QOSForm(request.POST)
            if form.is_valid():
                site = request.POST.get('site')
                result = qos_view_result(site)
                for r in result:
                    data_list.append(result[r][0].result)
                print(data_list)
                return render(request, 'dashboard/show_result.html', {'data': data_list})
        else:
            form = QOSForm()

    return render(request, 'dashboard/show_result.html', {'form': form})


@login_required
def services(request):
    if request.method == 'POST':
        nr = start_nornir('mza-infra')
        form = DCAccessForm(request.POST)
        if form.is_valid():
            group = request.POST.get('domain')
            tenant = request.POST.get('tenant')
            site = request.POST.get('site')
            hosts = nr.filter(role=group, site=site)
            data_list = []
            if group == "dc-access":
                result = hosts.run(task=dc_access_template, tenant=tenant)
                for r in result:
                    data_list.append(result[r][1])
            elif group == "dc-aggregation":
                result = hosts.run(task=dc_agg_template, tenant=tenant)
                for r in result:
                    data_list.append(result[r][1])
                    data_list.append(result[r][2])
            return render(request, 'dashboard/dc_access_template.html', {'data': data_list})
    else:
        form = DCAccessForm()

    return render(request, 'dashboard/services_config_list.html', {'form': form})
