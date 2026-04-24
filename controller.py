"""
controller.py – POX SDN Controller: Static Routing + Firewall (FIXED)
"""

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr
from pox.lib.util import dpid_to_str

log = core.getLogger()

# Constants
S1_DPID = 1
S2_DPID = 2

S1_PORT_H1 = 1
S1_PORT_H2 = 2
S1_PORT_S2 = 3

S2_PORT_H3 = 1
S2_PORT_H4 = 2
S2_PORT_S1 = 3

H1 = IPAddr('10.0.0.1')
H2 = IPAddr('10.0.0.2')
H3 = IPAddr('10.0.0.3')
H4 = IPAddr('10.0.0.4')

IPV4 = 0x0800
ARP = 0x0806

PRI_DROP = 200
PRI_ALLOW = 100
PRI_ARP = 50

def create_ip_match(src_ip, dst_ip):
    """Exact match for IPv4 src/dst"""
    m = of.ofp_match()
    m.dl_type = IPV4
    m.nw_src = src_ip
    m.nw_dst = dst_ip
    m.wildcards = 0  # Exact match
    return m

def install_flow(connection, match, out_port, priority):
    """Install a flow with action output to port"""
    msg = of.ofp_flow_mod()
    msg.match = match
    msg.priority = priority
    if out_port is None:
        # DROP rule - no actions
        pass
    else:
        msg.actions.append(of.ofp_action_output(port=out_port))
    connection.send(msg)

def install_arp_flood(connection):
    """Flood ARP packets"""
    msg = of.ofp_flow_mod()
    msg.match = of.ofp_match()
    msg.match.dl_type = ARP
    msg.priority = PRI_ARP
    msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
    connection.send(msg)

def install_s1_flows(conn):
    log.info("=== Installing flows on S1 (dpid=1) ===")
    
    # DROP rules (priority 200)
    install_flow(conn, create_ip_match(H2, H4), None, PRI_DROP)
    log.info("  DROP h2->h4")
    install_flow(conn, create_ip_match(H4, H2), None, PRI_DROP)
    log.info("  DROP h4->h2")
    
    # ALLOW rules (priority 100)
    install_flow(conn, create_ip_match(H1, H3), S1_PORT_S2, PRI_ALLOW)
    install_flow(conn, create_ip_match(H3, H1), S1_PORT_H1, PRI_ALLOW)
    install_flow(conn, create_ip_match(H1, H2), S1_PORT_H2, PRI_ALLOW)
    install_flow(conn, create_ip_match(H2, H1), S1_PORT_H1, PRI_ALLOW)
    install_flow(conn, create_ip_match(H2, H3), S1_PORT_S2, PRI_ALLOW)
    install_flow(conn, create_ip_match(H3, H2), S1_PORT_H2, PRI_ALLOW)
    install_flow(conn, create_ip_match(H1, H4), S1_PORT_S2, PRI_ALLOW)
    install_flow(conn, create_ip_match(H4, H1), S1_PORT_H1, PRI_ALLOW)
    
    install_arp_flood(conn)
    log.info("=== S1 flows installed ===\n")

def install_s2_flows(conn):
    log.info("=== Installing flows on S2 (dpid=2) ===")
    
    # DROP rules (priority 200)
    install_flow(conn, create_ip_match(H2, H4), None, PRI_DROP)
    log.info("  DROP h2->h4")
    install_flow(conn, create_ip_match(H4, H2), None, PRI_DROP)
    log.info("  DROP h4->h2")
    
    # ALLOW rules (priority 100)
    install_flow(conn, create_ip_match(H1, H3), S2_PORT_H3, PRI_ALLOW)
    install_flow(conn, create_ip_match(H3, H1), S2_PORT_S1, PRI_ALLOW)
    install_flow(conn, create_ip_match(H3, H4), S2_PORT_H4, PRI_ALLOW)
    install_flow(conn, create_ip_match(H4, H3), S2_PORT_H3, PRI_ALLOW)
    install_flow(conn, create_ip_match(H2, H3), S2_PORT_H3, PRI_ALLOW)
    install_flow(conn, create_ip_match(H3, H2), S2_PORT_S1, PRI_ALLOW)
    install_flow(conn, create_ip_match(H1, H4), S2_PORT_H4, PRI_ALLOW)
    install_flow(conn, create_ip_match(H4, H1), S2_PORT_S1, PRI_ALLOW)
    
    install_arp_flood(conn)
    log.info("=== S2 flows installed ===\n")

class SwitchHandler(object):
    def __init__(self, connection):
        self.connection = connection
        self.dpid = connection.dpid
        connection.addListeners(self)
        log.info("Switch connected: dpid=%s" % dpid_to_str(self.dpid))
        self._install_flows()
    
    def _install_flows(self):
        if self.dpid == S1_DPID:
            install_s1_flows(self.connection)
        elif self.dpid == S2_DPID:
            install_s2_flows(self.connection)
    
    def _handle_PacketIn(self, event):
        log.warning("PacketIn on dpid=%s (should not happen with proactive rules)" % 
                   dpid_to_str(self.dpid))

class StaticRoutingController(object):
    def __init__(self):
        core.openflow.addListeners(self)
        log.info("Static Routing SDN Controller STARTED")
    
    def _handle_ConnectionUp(self, event):
        SwitchHandler(event.connection)

def launch():
    core.registerNew(StaticRoutingController)
