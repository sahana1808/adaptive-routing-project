from mininet.net import Mininet
from mininet.node import Controller
from mininet.cli import CLI
from mininet.log import setLogLevel


def create_topology():
    net = Mininet(controller=Controller)

    print("Creating network...")

    # Add controller
    net.addController("c0")

    # Add hosts
    h1 = net.addHost("h1", ip="10.0.0.1/24")
    h2 = net.addHost("h2", ip="10.0.0.2/24")

    # Add switches
    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")

    # Add links
    net.addLink(h1, s1)
    net.addLink(s1, s2)
    net.addLink(s2, h2)

    net.start()

    print("\nNetwork started successfully!")
    print("Topology: h1 --- s1 --- s2 --- h2\n")

    CLI(net)

    net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    create_topology()
