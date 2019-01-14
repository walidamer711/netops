from ciscoconfparse import CiscoConfParse
import re
from nornir.plugins.tasks import networking
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F
from operator import itemgetter




def config_backup(task):
    r = task.run(task=networking.napalm_get, getters=["config"])
    #with open(f"backup/{task.host.name}.txt", "w") as f:
    #    f.write(r.result['config']['running'])
    confile = r.result['config']['running']
    #with open(f"backup/{task.host.name}.txt", "r") as f:
    #    confile = f.read()
    parse = CiscoConfParse(confile.splitlines())
    print(parse)
    CL_RE = re.compile(r'^\sclass\s\S*')
    data = {}
    cl = []
    for obj in parse.find_objects(CL_RE):
        c = {}
        cl_name = obj.re_match(r'^\sclass\s(\S*)')
        cir = obj.re_match_iter_typed(r'^\s+police\scir\s(\d*).+', default='')
        if cir:
            c['class'] = cl_name
            c['cir'] = cir
            cl.append(c)
            data['host'] = task.host.name
            data['result'] = cl
    task.host['qos'] = cl
    return data

def test_int_qos(nr):
    site = "mv1"
    if site == "mv1":
        site1 = "mv1"
        site2 = "mv3"
    else:
        site1 = "mv2"
        site2 = "mv2"
    hosts = nr.filter(F(role='internet-access') & F(site=site1) | F(role='internet-access') & F(site=site2))
    hosts.run(task=config_backup)
    qos = []
    for host in hosts.inventory.hosts.values():
        qos.append(sorted(host['qos'], key=itemgetter("class")))
    assert qos[0] == qos[1]

