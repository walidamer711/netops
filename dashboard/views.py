from django.shortcuts import render, HttpResponse
from napalm import get_network_driver

# Create your views here.

def index(request):
    if request.method == 'GET':
        return render(request, 'index.html')
    if request.method == 'POST':
        ip = request.POST.get("ip")
        user = request.POST.get("user")
        password = request.POST.get("password")
        driver = get_network_driver('nxos_ssh')

        with driver(ip, user, password) as device:
            interfaces = device.get_interfaces()

        return render(request, 'submit.html', {'int':interfaces})

def home(request):
    return render(request, 'home.html')