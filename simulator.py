


class Node:
  def __init__(self, mac, ip, mtu, gateway):
    self.mac = mac
    self.ip = ip
    self.mtu = mtu
    self.gateway = gateway

class Router:
  def __init__(self, mac, ip, mtu, gateway):
    self.mac = mac
    self.ip = ip
    self.mtu = mtu
    self.gateway = gateway












def main():
    file = open("topologia.txt", "r")
    for line in file:
        print(line)

    file.close() 

main()

