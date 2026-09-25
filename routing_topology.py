from mininet.net import Mininet
from mininet.node import Controller, Node
from mininet.cli import CLI
from mininet.log import setLogLevel


class LinuxRouter(Node):
    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()


def create_topology():
    net = Mininet(controller=Controller)

    net.addController("c0")

    # Hosts
    h1 = net.addHost("h1")
    h2 = net.addHost("h2")

    # Routers
    r1 = net.addHost("r1", cls=LinuxRouter)
    r2 = net.addHost("r2", cls=LinuxRouter)
    r3 = net.addHost("r3", cls=LinuxRouter)

    # Links
    net.addLink(h1, r1)
    net.addLink(r1, r2)
    net.addLink(r1, r3)
    net.addLink(r2, r3)
    net.addLink(r3, h2)

    net.start()

    # h1 network
    h1.setIP("10.0.1.10/24", intf="h1-eth0")
    h1.cmd("ip route add default via 10.0.1.1")

    # r1
    r1.setIP("10.0.1.1/24", intf="r1-eth0")
    r1.setIP("10.0.2.1/30", intf="r1-eth1")
    r1.setIP("10.0.3.1/30", intf="r1-eth2")

    # r2
    r2.setIP("10.0.2.2/30", intf="r2-eth0")
    r2.setIP("10.0.5.1/30", intf="r2-eth1")

    # r3
    r3.setIP("10.0.3.2/30", intf="r3-eth0")
    r3.setIP("10.0.5.2/30", intf="r3-eth1")
    r3.setIP("10.0.4.1/24", intf="r3-eth2")

    # h2 network
    h2.setIP("10.0.4.10/24", intf="h2-eth0")
    h2.cmd("ip route add default via 10.0.4.1")

    # Routes to h1 network
    r2.cmd("ip route add 10.0.1.0/24 via 10.0.2.1")
    r3.cmd("ip route add 10.0.1.0/24 via 10.0.3.1")

    # Route from r1 to h2 via r3
    r1.cmd("ip route add 10.0.4.0/24 via 10.0.3.2")

    # Route from r2 to h2 via r3
    r2.cmd("ip route add 10.0.4.0/24 via 10.0.5.2")

    print("\nRouting topology started successfully!")
    print("Path 1: h1 -> r1 -> r3 -> h2")
    print("Path 2: h1 -> r1 -> r2 -> r3 -> h2")
    print()

    CLI(net)
    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    create_topology()
