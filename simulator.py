
import sys
import re


class Node:
  def __init__(self,name, id, mac, ip, mtu, gateway):
    self.id = id
    self.name = name
    self.mac = mac
    self.ip = ip
    self.mtu = mtu
    self.gateway = gateway

class Router:


    def __init__(self,id, name, mac = [], ip = [], mtu = [] ):
        self.id = id
        self.name = name
        self.mac = mac
        self.ip = ip
        self.mtu = mtu
        self.table = {}




def find_router_id_by_name(routers, name):
    for r in routers:
        if r.name == name:
            return r.id
    
    return -2


def read_file(name, nodes, routers):
    file = open(name, "r")
    type = 0
    id = 0


    for line in file:
        if '#NODE' in line:
            type = 1
            continue
        elif '#ROUTERTABLE' in line:
            type = 3
            continue
        elif '#ROUTER' in line:
            type = 2
            id = 0
            continue
        
        if type == 1:
            splited_line = re.split(',|\n', line)
            nodes.append(Node(id, splited_line[0], splited_line[1], splited_line[2], splited_line[3], splited_line[4]))
            id += 1

        if type == 2:
            splited_line = re.split(',|\n', line)
            router = Router(id, splited_line[0])
            length = int(splited_line[1]) * 3
            splited_line = splited_line[2:]

            for i in range(0, length, 3):
                router.mac.append(splited_line[i])
                router.ip.append(splited_line[i+1])
                router.mtu.append(splited_line[i+2]) 

            routers.append(router)
            id += 1
        
        if type == 3:
            splited_line = re.split(',|\n', line)
            name = splited_line[0]
            id = find_router_id_by_name(routers, name)

            next_hope = splited_line[2] + ':' + splited_line[3]
            routers[id].table[splited_line[1]] = next_hope


    file.close() 










def main():

    topology, source, destination, message = sys.argv[1:]

    nodes = []
    routers = []
    read_file(topology, nodes, routers)




    for n in nodes:
        print(f"node {n.name} -> mac:{n.mac}, ip:{n.ip}, mtu:{n.mtu}, gateway:{n.gateway}")

    for r in routers:
        print(f"router {r.name} -> mac:{r.mac}, ip:{r.ip}, mtu:{r.mtu}, table{r.table}")


    

main()

