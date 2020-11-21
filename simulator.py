
import sys
import re


class Node:
  def __init__(self,id, name, mac, ip, mtu, gateway):
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

def find_node_id_by_name(nodes, name):
    for n in nodes:
        if n.name == name:
            return n.id
    
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
            continue
        
        if type == 1:
            splited_line = re.split(',|\n', line)
            nodes.append(Node(id, splited_line[0], splited_line[1], splited_line[2], splited_line[3], splited_line[4]))
            id += 1

        if type == 2:
            splited_line = re.split(',|\n', line)
            name = splited_line[0]
            router = Router(id, name)
            length = int(splited_line[1]) * 3
            splited_line = splited_line[2:]

            for i in range(0, length, 3):
                nodes.append(Node(id, name, splited_line[i], splited_line[i+1], splited_line[i+2], splited_line[i+1]))
                router.mac.append(splited_line[i])
                router.ip.append(splited_line[i+1])
                router.mtu.append(splited_line[i+2]) 
                id += 1

            routers.append(router)
            id += 1
        
        # if type == 3:
        #     splited_line = re.split(',|\n', line)
        #     name = splited_line[0]
        #     id = find_router_id_by_name(routers, name)

        #     next_hope = splited_line[2] + ':' + splited_line[3]
        #     routers[id].table[splited_line[1]] = next_hope


    file.close() 



def get_net(ip):
    bar = ip[len(ip)-2:]

    net = ip[:(len(ip)-3)].split(".")
    bin_net = ''
    int_net = [int(i) for i in net]
    result = ''


    for i in int_net:
        bin_net += bin(i)[2:].zfill(8)

    bin_net = bin_net[:int(bar)]


    
    for i in range(8,len(bin_net), 9):
        bin_net = bin_net[:i] + '.' + bin_net[i:]

    net = bin_net.split('.')
    for b in net:
        result += '.' + str(int(b,2))
    result = result[1:]


    return result



def arp_request (nodes, src, dest_ip):


    print(f"{src.name} box {src.name} : ETH (src=:{src.mac} dst=:FF) \\n ARP - Who has {dest_ip}? Tell {dest_ip};")

    nodes_destinations = []
    
    #send broadcast

    #get all nodes in source node gateway
    for n in nodes:
        if n.id != src.id:
            nodes_destinations.append(n) 
    

    return nodes_destinations
    
    
def arp_reply(nodes_receving, src, dest_ip, fin_dest):

    #check if a node is the destination
    for n in nodes_receving:
        if n.ip[:len(n.ip)-3] == dest_ip:
            print(f"{n.name} => {src.name} : ETH (src={n.mac} dst={src.mac}) \\n ARP - {n.ip[:len(n.ip)-3]} is at {n.mac};")
            return n

    
    
    return None









def main():

    topology, source, destination, message = sys.argv[1:]

    nodes = []
    routers = []
    read_file(topology, nodes, routers)

    

    id_src = find_node_id_by_name(nodes, source)
    id_dest = find_node_id_by_name(nodes, destination)
    node_src = nodes[id_src]
    node_dest = nodes[id_dest]
    ttl = 8

    current_node = node_src
    end = False
    
    current_net = get_net(node_src.ip)

    while not end:
        if ttl == 0:
            break

     

        #ARP request
        nodes_in_same_net = [n for n in nodes if current_net in n.ip and current_node.id != n.id]
        routers_in_same_net = []

        for r in routers:
            for i in r.ip:
                if current_net in i :
                    routers_in_same_net.append(r)
        
        if current_net in node_dest.ip:
            ip =  node_dest.ip[:len(node_dest.ip)-3]
            end = True
        else:
            ip = current_node.gateway[:len(current_node.gateway)-3]
            
        

        nodes_destinations = arp_request(nodes_in_same_net, current_node, ip)
        

        #ARP reply

        current_node = arp_reply(nodes_destinations, current_node, ip, node_dest)

        

        ttl -= 1
   



        # nodes_destinations, routers_destinations = [],[]
        # for ip in next_ip:
        #     # ARP request
            
        #     nodes_aux, routers_aux = arp_request(nodes, routers, node_src, ip)
        #     nodes_destinations.extend(nodes_aux)
        #     routers_destinations.extend(routers_aux)
        
        # #ARP reply
        # end, next_router = arp_reply(nodes_destinations, routers_destinations, current_node, ip, node_dest)

        # next_ip = []
        # for i in next_router.ip:
        #     next_ip.append(i[:len(i)-3])
        # print(next_ip)
        
  
        

    
    



    # for n in nodes:
    #     print(f"{n.id}  node {n.name} -> mac:{n.mac}, ip:{n.ip}, mtu:{n.mtu}, gateway:{n.gateway}")

    # for r in routers:
    #     print(f"router {r.name} -> mac:{r.mac}, ip:{r.ip}, mtu:{r.mtu}, table{r.table}")


    

main()

