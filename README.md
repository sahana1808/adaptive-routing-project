# Adaptive Network Routing & Traffic Monitoring System

A Mininet-based network simulation that demonstrates adaptive routing under changing network conditions. The system monitors end-to-end latency and automatically switches between two available routes when congestion causes high latency.

---

## Project Overview

This project simulates a small routed network with multiple paths between a source host and destination host.

The system:

- Builds a multi-router topology using Mininet
- Configures Linux routers with IP forwarding
- Provides two possible paths between the source and destination
- Simulates network congestion using Linux `tc` and `netem`
- Measures end-to-end network latency
- Detects high-latency conditions
- Automatically switches to an alternate route
- Switches back to the primary route when network conditions recover

---

## Network Topology

```text
             r2
            /  \
           /    \
h1 ---- r1      r3 ---- h2
