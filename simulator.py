
import sys
import re


class Node:
  def __init__(self,id, name, mac, ip, mtu, gateway, node):
    self.id = id
    self.name = name
    self.mac = mac
    self.ip = ip
    self.mtu = mtu
    self.gateway = gateway
    self.node = node

class Router:


    def __init__(self,id, name, mac = [], ip = [], mtu = [], gates = [] ):
        self.id = id
        self.name = name
        self.mac = mac
        self.ip = ip
        self.mtu = mtu
        self.table = {}
        self.gates = gates




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
            id_r = 0
            continue
        
        if type == 1:
            splited_line = re.split(',|\n', line)
            nodes.append(Node(id, splited_line[0], splited_line[1], splited_line[2], splited_line[3], splited_line[4], True))
            id += 1

        if type == 2:
            splited_line = re.split(',|\n', line)
            name = splited_line[0]
            router = Router(id_r, name)
            length = int(splited_line[1]) * 3
            splited_line = splited_line[2:]

            for i in range(0, length, 3):
                gate = Node(id, name, splited_line[i], splited_line[i+1], splited_line[i+2], splited_line[i+1], False)
                nodes.append(gate)
                router.mac.append(splited_line[i])
                router.ip.append(splited_line[i+1])
                router.mtu.append(splited_line[i+2])
                router.gates.append(gate) 
                id += 1

            routers.append(router)
            id += 1
            id_r += 1
        
        if type == 3:
            splited_line = re.split(',|\n', line)
            name = splited_line[0]
            id = find_router_id_by_name(routers, name)

            next_hope = splited_line[2] + ':' + splited_line[3]
            routers[id].table[splited_line[1]] = next_hope


    file.close() 


def get_node_by_ip(nodes, ip):
    for n in nodes:
        if n.ip == ip:
            return n


def get_net(ip):
    bar = ip.split('/')[1]

    net = ip.split('/')[0].split(".")
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

def generate_mask(net):

    vet_net = net.split('.')
    
    while len(vet_net) < 4:
        vet_net.append('0')

    
    result = ''
    for i in vet_net:
        result += '.' + i

    return result[1:]


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
        aux = n.ip.split('/')[0]
        print(f'{aux} == {dest_ip}:')
        if n.ip.split('/')[0] == dest_ip:
            print(f"{n.name} => {src.name} : ETH (src={n.mac} dst={src.mac}) \\n ARP - {n.ip.split('/')[0]} is at {n.mac};")
            return n


    
    return None




def send_message(message, node_src, node_dest, ttl):
    ip_src = node_src.ip.split('/')[0]
    ip_dest = node_dest.ip.split('/')[0]
    print(f'{node_src.name} => {node_dest.name} : ETH (src={node_src.mac} dst=:{node_dest.mac} \\n IP (src={ip_src} dst={ip_dest} ttl={ttl} mf={node_dest.mtu} off=0) \n ICMP - Echo request (data={message});')
 




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
    path = [node_src]
    

    while not end:
        if ttl == 0:
            break

        node_src = current_node
        current_net = get_net(node_src.ip)
        #ARP request
        nodes_in_same_net = [n for n in nodes if current_net in n.ip and current_node.id != n.id]
        routers_in_same_net = []

        for r in routers:
            for i in r.ip:
                if current_net in i :
                    routers_in_same_net.append(r)
        
        if current_net in node_dest.ip:
            ip =  node_dest.ip.split('/')[0]
            end = True
            
        else:
            ip = current_node.gateway.split('/')[0]
            
        

        nodes_destinations = arp_request(nodes_in_same_net, current_node, ip)
        
        if not current_node.node:
            nodes_destinations.append(current_node)
        #ARP reply

        current_node = arp_reply(nodes_destinations, current_node, ip, node_dest)

        message_list = [message]
        mtu = int(current_node.mtu)
        if len(message) > mtu:
            message_list = []
            slices = (len(message)//mtu) + 1
            for i in range(slices):
                if i == slices:
                    message_list.append(message[i*mtu:])
                else:
                    message_list.append(message[i*mtu:i*mtu+mtu])



        for m in message_list:
            send_message(m, node_src, current_node, ttl)

        if(current_node.node):
            if end:
                print(f'{node_dest.name} rbox {node_dest.name} : Received {message};')
        
            path.append(current_node)
            ttl -= 1
            continue
        r_id = find_router_id_by_name(routers, current_node.name)



        mask = generate_mask(get_net(node_dest.ip))
        mask += '/' + node_src.ip.split('/')[1]
       
 
        ip_dest = routers[r_id].table.get(mask)
        
        if type (ip_dest) == type(None):
            ip_dest = routers[r_id].table['0.0.0.0/0']
 

        index = ip_dest.split(':')[1]
        

 
    
        current_node = get_node_by_ip(nodes,routers[r_id].gates[int(index)].ip)

    
        path.append(current_node)


        ttl -= 1
   
    ttl = 8
    path.reverse()
    for n_s, n_d in zip(path, path[1:]):
        send_message(message, n_s, n_d, ttl)
        ttl -= 1

    print(f'{path[-1].name} rbox {path[-1].name} : Received {message};')

        
    

main()

