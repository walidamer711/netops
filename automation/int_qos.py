from ciscoconfparse import CiscoConfParse
import re
from nornir.plugins.tasks import networking
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F
from .helper import start_nornir


def config_backup(task):
    r = task.run(task=networking.napalm_get, getters=["config"])
    #with open(f"backup/{task.host.name}.txt", "w") as f:
    #    f.write(r.result['config']['running'])
    confile = r.result['config']['running']
    #with open(f"backup/{task.host.name}.txt", "r") as f:
    #    confile = f.read()
    parse = CiscoConfParse(confile.splitlines())
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
    return data

def qos_view_result(site):
    nr = start_nornir('mza-infra')
    hosts = nr.filter(F(role='internet-access') & F(site=site))
    result = hosts.run(task=config_backup)
    return result


def main():
    #nr = start_nornir('mza-infra')
    #h = nr.filter(role='internet-access')
    #r = h.run(task=config_backup)
    #print_result(r)
    result = qos_view_result("mv1")

    for r in result:
        print(result[r][0].result['result'])
        for x in result[r][0].result['result']:
            print(x['class'])
            print(int(x['cir']))







if __name__ == '__main__':
    main()