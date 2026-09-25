# Adaptive Network Routing & Traffic Monitoring System

A Mininet-based network simulation that demonstrates adaptive routing under changing network conditions. The system monitors network latency, measures throughput using `iperf3`, simulates congestion, and automatically switches between available routes when network performance degrades.

---

## Project Overview

This project simulates a routed computer network with multiple paths between a source host and a destination host.

The project demonstrates how network performance can be monitored and used to make adaptive routing decisions.

The system:

- Builds a multi-router topology using Mininet
- Configures Linux routers with IP forwarding
- Provides two possible paths between the source and destination
- Uses static routing to establish primary and alternate paths
- Simulates network congestion using Linux `tc` and `netem`
- Measures end-to-end latency using ICMP ping
- Measures network throughput using `iperf3`
- Detects high-latency conditions
- Automatically switches to an alternate route
- Switches back to the primary route when network conditions recover
- Uses Linux routing tables to dynamically change the next hop

---

## Network Topology

```text
             r2
            /  \
           /    \
          /      \
h1 ---- r1        r3 ---- h2
````

### Available Paths

#### Primary Path

```text
h1 → r1 → r3 → h2
```

#### Alternate Path

```text
h1 → r1 → r2 → r3 → h2
```

The primary path directly connects `r1` to `r3`.

The alternate path uses `r2` before reaching `r3`.

---

## IP Addressing

| Device | Interface | IP Address   |
| ------ | --------- | ------------ |
| h1     | h1-eth0   | 10.0.1.10/24 |
| r1     | r1-eth0   | 10.0.1.1/24  |
| r1     | r1-eth1   | 10.0.2.1/30  |
| r1     | r1-eth2   | 10.0.3.1/30  |
| r2     | r2-eth0   | 10.0.2.2/30  |
| r2     | r2-eth1   | 10.0.5.1/30  |
| r3     | r3-eth0   | 10.0.3.2/30  |
| r3     | r3-eth1   | 10.0.5.2/30  |
| r3     | r3-eth2   | 10.0.4.1/24  |
| h2     | h2-eth0   | 10.0.4.10/24 |

---

## Technologies Used

* Python 3
* Mininet
* Linux Networking
* Open vSwitch
* Linux IP Routing
* Linux Network Namespaces
* `ip` routing commands
* `tc` / `netem`
* ICMP Ping
* Traceroute
* `iperf3`
* Git
* GitHub
* WSL2 on Windows

---

## Project Structure

```text
adaptive-routing-project/
│
├── topology.py
├── routing_topology.py
├── monitor.py
├── adaptive_router.py
├── .gitignore
└── README.md
```

### File Description

| File                  | Purpose                                                      |
| --------------------- | ------------------------------------------------------------ |
| `topology.py`         | Basic Mininet topology used for initial network testing      |
| `routing_topology.py` | Creates the multi-router routed network                      |
| `monitor.py`          | Continuously measures end-to-end latency                     |
| `adaptive_router.py`  | Automatically switches routes based on measured latency      |
| `.gitignore`          | Prevents temporary Python and log files from being committed |
| `README.md`           | Project documentation                                        |

---

## Routing Architecture

The network uses Linux routers implemented as Mininet `Node` objects.

IP forwarding is enabled on the routers so that packets can travel between different IP subnets.

Router `r1` has two possible next hops for reaching the destination network:

```text
Primary Next Hop:
10.0.3.2
```

```text
Alternate Next Hop:
10.0.2.2
```

The destination network is:

```text
10.0.4.0/24
```

### Primary Route

```text
10.0.4.0/24 via 10.0.3.2
```

Resulting path:

```text
h1 → r1 → r3 → h2
```

### Alternate Route

```text
10.0.4.0/24 via 10.0.2.2
```

Resulting path:

```text
h1 → r1 → r2 → r3 → h2
```

---

## Adaptive Routing Logic

The adaptive routing controller continuously measures the latency between `h1` and `h2`.

A threshold of:

```text
50 ms
```

is used to determine whether the network is experiencing high latency.

### Routing Decision

```text
                Measure Latency
                       |
                       v
                Latency > 50 ms?
                  /          \
                Yes            No
                 |              |
                 v              v
        Switch to Alternate   Keep Current
             Route              Route
                 |
                 v
          Monitor Again
                 |
                 v
         Network Recovers
                 |
                 v
        Switch to Primary
```

### High Latency Condition

When latency exceeds 50 ms:

```text
h1 → r1 → r3 → h2
          X
      Congested
```

The controller changes the route to:

```text
h1 → r1 → r2 → r3 → h2
```

### Recovery Condition

When latency falls below the threshold again, the controller switches back to:

```text
h1 → r1 → r3 → h2
```

---

## Latency Monitoring

The `monitor.py` program periodically sends ICMP ping packets from the Mininet `h1` namespace to `h2`.

Example normal output:

```text
Current latency: 1.20 ms
Network condition: NORMAL
----------------------------------------
```

When congestion is detected:

```text
Current latency: 105.40 ms
HIGH LATENCY DETECTED
Recommended action: Switch to alternate route
----------------------------------------
```

---

## Congestion Simulation

Network congestion is simulated using Linux `tc` and `netem`.

The primary link between `r1` and `r3` is:

```text
r1-eth2
```

Artificial congestion can be introduced using:

```bash
r1 tc qdisc add dev r1-eth2 root netem delay 100ms rate 1mbit
```

This introduces approximately:

* 100 ms artificial delay
* 1 Mbps rate limitation

The congestion can be removed using:

```bash
r1 tc qdisc del dev r1-eth2 root
```

The link can be verified using:

```bash
r1 tc qdisc show dev r1-eth2
```

A normal link shows:

```text
qdisc noqueue 0: root refcnt 2
```

---

## Throughput Testing with iperf3

The project uses `iperf3` to measure TCP throughput between `h1` and `h2`.

### Start the iperf3 Server

Inside Mininet:

```bash
h2 iperf3 -s -D
```

### Run the Client

From `h1`:

```bash
h1 iperf3 -c 10.0.4.10 -t 10
```

This measures the throughput between the source and destination hosts.

---

## Experimental Results

### 1. Normal Network Condition

A baseline throughput test was performed without artificial congestion.

Observed result:

```text
Average Throughput: 1.11 Gbit/s
Data Transferred: 1.29 GBytes
Retransmissions: 0
```

This demonstrates that the routed network can successfully transfer high-volume TCP traffic under normal conditions.

---

### 2. Network Under Congestion

Artificial congestion was introduced on the primary `r1 → r3` link:

```bash
r1 tc qdisc add dev r1-eth2 root netem delay 100ms rate 1mbit
```

A throughput test was then performed.

Observed result before the connection was interrupted:

```text
Throughput: approximately 3.13 Mbit/s
```

The test also demonstrated that severe delay and rate limiting can significantly degrade TCP throughput.

---

### 3. Network Recovery

The artificial congestion was removed:

```bash
r1 tc qdisc del dev r1-eth2 root
```

The network was tested again.

Observed result:

```text
Throughput: 717 Mbit/s
Retransmissions: 0
```

The successful recovery confirms that the network returned to normal operating conditions after removing the artificial congestion.

---

## Adaptive Routing Experiment

The adaptive controller was tested while the primary route was experiencing artificial congestion.

Example controller behavior:

```text
Measured latency: 118.63 ms
HIGH LATENCY DETECTED
Switching to alternate route...

Route changed:
h1 -> r1 -> r2 -> r3 -> h2
```

After switching:

```text
Measured latency: 6.19 ms
```

When the network recovered:

```text
Network recovered
Switching back to primary route...

Route changed:
h1 -> r1 -> r3 -> h2
```

The controller successfully detected repeated high-latency conditions and automatically switched between the primary and alternate routes.

---

## Experimental Summary

| Network Condition               |       Observed Result |
| ------------------------------- | --------------------: |
| Normal throughput test          |           1.11 Gbit/s |
| Congested throughput test       |          ~3.13 Mbit/s |
| Recovered throughput test       |            717 Mbit/s |
| Normal latency                  | Low millisecond range |
| Congested latency               |              ~100+ ms |
| Retransmissions in normal tests |                     0 |
| Automatic route switching       |            Successful |

> Note: Throughput values can vary between runs because the project is running inside WSL2 and depends on the host system's available resources.

---

## Running the Project

### 1. Start the Network

Open WSL and run:

```bash
cd ~/adaptive-routing-project
sudo python3 routing_topology.py
```

This starts the Mininet network and opens the Mininet CLI.

---

### 2. Test Connectivity

Inside the Mininet CLI:

```bash
h1 ping -c 5 10.0.4.10
```

The expected result is successful communication between `h1` and `h2`.

---

### 3. Check the Primary Route

Run:

```bash
h1 traceroute -n 10.0.4.10
```

The expected route is:

```text
h1 → r1 → r3 → h2
```

---

### 4. Start the iperf3 Server

Inside Mininet:

```bash
h2 iperf3 -s -D
```

---

### 5. Run an iperf3 Throughput Test

Inside Mininet:

```bash
h1 iperf3 -c 10.0.4.10 -t 10
```

---

### 6. Find Mininet Process IDs

Inside the Mininet CLI:

```bash
h1 sh -c 'echo $PPID'
```

and:

```bash
r1 sh -c 'echo $PPID'
```

Save the returned process IDs.

---

### 7. Run the Latency Monitor

Open another WSL terminal:

```bash
cd ~/adaptive-routing-project
python3 monitor.py <h1_pid>
```

Example:

```bash
python3 monitor.py 21182
```

The monitor continuously reports the current network latency.

---

### 8. Simulate Congestion

Inside Mininet:

```bash
r1 tc qdisc add dev r1-eth2 root netem delay 100ms rate 1mbit
```

---

### 9. Run the Adaptive Routing Controller

Open another WSL terminal:

```bash
cd ~/adaptive-routing-project
python3 adaptive_router.py <h1_pid> <r1_pid>
```

Example:

```bash
python3 adaptive_router.py 21182 21188
```

The controller will continuously monitor latency and automatically change the route when the threshold is exceeded.

---

### 10. Remove Simulated Congestion

After testing:

```bash
r1 tc qdisc del dev r1-eth2 root
```

Verify:

```bash
r1 tc qdisc show dev r1-eth2
```

Expected:

```text
qdisc noqueue 0: root refcnt 2
```

---

## Key Networking Concepts Demonstrated

* IP addressing
* Subnetting
* Static routing
* Next-hop routing
* Routing tables
* Linux IP forwarding
* Multi-path routing
* Network congestion
* Latency monitoring
* Throughput measurement
* TCP performance
* Traceroute
* Dynamic route selection
* Network performance monitoring
* Automated route switching
* Linux traffic control
* Mininet network emulation
* Network namespaces

---

## Project Workflow

```text
             Start Mininet Network
                      |
                      v
              Establish Routes
                      |
                      v
              Test Connectivity
                      |
                      v
              Monitor Latency
                      |
                      v
            +-------------------+
            | Latency > 50 ms ? |
            +-------------------+
                 /         \
               Yes           No
                |             |
                v             v
       Switch to Alternate   Keep
             Route          Current Route
                |
                v
          Monitor Again
                |
                v
        Network Conditions
             Recover
                |
                v
        Switch to Primary
             Route
```

---

## Project Validation

The project was validated using:

* `ping` for connectivity and latency
* `traceroute` for path verification
* `tc/netem` for congestion simulation
* `iperf3` for throughput measurement
* Linux routing tables for route changes
* Automated route switching using Python

The primary and alternate paths were independently verified using traceroute.

The adaptive controller was tested under artificial congestion and successfully switched routes based on the configured latency threshold.

---

## Limitations

The current implementation uses a **latency-threshold based routing decision**.

It does not currently calculate a shortest path dynamically using Dijkstra's algorithm or an actual routing protocol such as OSPF.

The current implementation also uses end-to-end latency as the primary decision metric rather than directly calculating link utilization.

---

## Future Improvements

Future versions can extend the system with:

* Dijkstra-based shortest-path calculation
* Real-time bandwidth utilization monitoring
* Packet-loss based route selection
* Automated throughput-based route selection
* Multiple routing metrics
* Automatic topology discovery
* OSPF-like dynamic routing
* Web-based network monitoring dashboard
* Route optimization using latency, packet loss and bandwidth
* Integration with a Software-Defined Networking controller
* Real-time network visualization

---

## Learning Outcomes

This project provided practical experience with:

* Computer Networks
* IP routing
* Routing tables
* Linux networking
* Network emulation
* Network congestion simulation
* TCP performance analysis
* Throughput measurement
* Latency monitoring
* Automated network management
* Python scripting
* Git and GitHub

The project demonstrates how network performance measurements can be used to dynamically select an alternate path when the current route experiences degraded conditions.

---

## Author

**Sahana B S**

Computer Science Engineering
KLE Technological University

GitHub:

[https://github.com/sahana1808/adaptive-routing-project](https://github.com/sahana1808/adaptive-routing-project)

```

