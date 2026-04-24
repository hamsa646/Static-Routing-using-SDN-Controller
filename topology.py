#!/usr/bin/env python3
"""
topo.py - Mininet Topology for SDN Static Routing Project
==========================================================
Project : Static Routing using SDN Controller (POX)
Author  : <Your Name>

Topology Diagram:
                     s1 (dpid=1)         s2 (dpid=2)
  h1 (10.0.0.1) ---[port 1]            [port 1]--- h3 (10.0.0.3)
  h2 (10.0.0.2) ---[port 2]  [port3]--[port3]  [port 2]--- h4 (10.0.0.4)

Port Mapping:
  s1 : port1 = h1 | port2 = h2 | port3 = s2
  s2 : port1 = h3 | port2 = h4 | port3 = s1

Traffic Policy (enforced by controller.py):
  ALLOWED : h1 <--> h3  (cross-switch, fully routed)
  ALLOWED : h1 <--> h2  (same switch)
  ALLOWED : h3 <--> h4  (same switch)
  ALLOWED : h2 <--> h3  (cross-switch, allowed)
  ALLOWED : h1 <--> h4  (cross-switch, allowed)
  BLOCKED : h2 <--> h4  (blocked by firewall rule - DROP)

Usage:
  sudo python3 topo.py
  (POX controller must already be running before this)
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink


# ─────────────────────────────────────────────
#  Custom Topology Class
# ─────────────────────────────────────────────
class SDNStaticRoutingTopo(Topo):
    """
    Two-switch linear topology with 4 hosts.
    Port numbers are explicitly set so the controller
    can use hardcoded static routing rules reliably.
    """

    def build(self):
        # ── Switches ──────────────────────────────
        # dpid must match S1_DPID / S2_DPID in controller.py
        s1 = self.addSwitch('s1', dpid='0000000000000001',
                            cls=OVSKernelSwitch, protocols='OpenFlow10')
        s2 = self.addSwitch('s2', dpid='0000000000000002',
                            cls=OVSKernelSwitch, protocols='OpenFlow10')

        # ── Hosts ─────────────────────────────────
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', ip='10.0.0.4/24', mac='00:00:00:00:00:04')

        # ── Links (explicit port numbers) ─────────
        # s1: port1=h1, port2=h2, port3=s2
        self.addLink(h1, s1, port1=0, port2=1)   # h1-eth0  <-> s1-eth1
        self.addLink(h2, s1, port1=0, port2=2)   # h2-eth0  <-> s1-eth2
        self.addLink(s1, s2, port1=3, port2=3)   # s1-eth3  <-> s2-eth3

        # s2: port1=h3, port2=h4, port3=s1
        self.addLink(h3, s2, port1=0, port2=1)   # h3-eth0  <-> s2-eth1
        self.addLink(h4, s2, port1=0, port2=2)   # h4-eth0  <-> s2-eth2


# ─────────────────────────────────────────────
#  Network Runner
# ─────────────────────────────────────────────
def run():
    """Build the network, start it, and open the Mininet CLI."""

    topo = SDNStaticRoutingTopo()

    net = Mininet(
        topo=topo,
        controller=RemoteController('c0', ip='127.0.0.1', port=6633),
        switch=OVSKernelSwitch,
        link=TCLink,
        autoSetMacs=False,   # We set MACs explicitly in the topo
        autoStaticArp=False  # Let the SDN controller handle ARP
    )

    net.start()

    # ── Print topology summary ─────────────────
    info("\n")
    info("=" * 58 + "\n")
    info("   SDN Static Routing Topology - STARTED\n")
    info("=" * 58 + "\n")
    info("  Hosts:\n")
    info("    h1 -> 10.0.0.1  (MAC: 00:00:00:00:00:01)\n")
    info("    h2 -> 10.0.0.2  (MAC: 00:00:00:00:00:02)\n")
    info("    h3 -> 10.0.0.3  (MAC: 00:00:00:00:00:03)\n")
    info("    h4 -> 10.0.0.4  (MAC: 00:00:00:00:00:04)\n")
    info("\n")
    info("  Switch Port Map:\n")
    info("    s1 : port1=h1 | port2=h2 | port3=s2\n")
    info("    s2 : port1=h3 | port2=h4 | port3=s1\n")
    info("\n")
    info("  Traffic Policy:\n")
    info("    [ALLOWED]  h1 <--> h3  (static route via s1-s2)\n")
    info("    [ALLOWED]  h1 <--> h2  (same switch s1)\n")
    info("    [ALLOWED]  h3 <--> h4  (same switch s2)\n")
    info("    [ALLOWED]  h2 <--> h3  (cross-switch)\n")
    info("    [ALLOWED]  h1 <--> h4  (cross-switch)\n")
    info("    [BLOCKED]  h2 <--> h4  (firewall DROP rule)\n")
    info("=" * 58 + "\n")
    info("\n")
    info("  Quick Test Commands:\n")
    info("    Scenario 1 (Allowed) : h1 ping h3\n")
    info("    Scenario 2 (Blocked) : h2 ping h4\n")
    info("    Flow table           : dpctl dump-flows\n")
    info("    iperf (allowed)      : iperf h1 h3\n")
    info("=" * 58 + "\n\n")

    # ── Open interactive CLI ───────────────────
    CLI(net)

    # ── Clean up ──────────────────────────────
    net.stop()
    info("Network stopped.\n")


# ─────────────────────────────────────────────
#  Entry Point
# ─────────────────────────────────────────────
if __name__ == '__main__':
    setLogLevel('info')
    run()


# ─────────────────────────────────────────────
#  Topo export (for: sudo mn --custom topo.py)
# ─────────────────────────────────────────────
topos = {'sdntopo': SDNStaticRoutingTopo}
