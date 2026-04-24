
#  Static Routing using SDN controller (using POX + Mininet)

---

##  Introduction

Software Defined Networking (SDN) is a networking paradigm that separates the control plane from the data plane, enabling centralized network control. Unlike traditional networks where each router independently makes decisions, SDN uses a centralized controller to manage the entire network.

In this project, SDN is implemented using the POX controller and Mininet emulator to demonstrate centralized routing, flow rule management, and traffic policy enforcement.

---

##  Problem Statement

Traditional networks rely on distributed routing protocols such as OSPF and RIP, which lead to:

- Complex configuration  
- Slow convergence  
- Limited control over traffic  

This project solves these issues using SDN by:

- Centralizing control using a POX controller  
- Installing flow rules using OpenFlow  
- Enforcing traffic policies (allow/block)  
- Operating proactively without continuous controller interaction  

---

##  Setup

### Requirements
- Mininet  
- Open vSwitch  
- Python 3  
- POX Controller  

### Installation
```bash
sudo apt-get update
sudo apt-get install -y mininet openvswitch-switch python3

git clone https://github.com/noxrepo/pox.git ~/pox
````

### Project Files

* topo.py → Mininet topology
* controller.py → POX controller

---

##  Overview

The network consists of:

* 2 switches (s1, s2)
* 4 hosts (h1, h2, h3, h4)

### Key Features

* Static routing using predefined paths
* Firewall policy (h2 ↔ h4 blocked)
* Centralized SDN control
* Proactive flow rule installation

---

##  Execution Steps

### Step 1 — Create Project Folder

```bash
mkdir ~/sdn_project
cd ~/sdn_project
```

### Step 2 — Add Files

```bash
nano topo.py
nano controller.py
```

### Step 3 — Copy Controller

```bash
cp ~/sdn_project/controller.py ~/pox/ext/controller.py
```

### Step 4 — Clean Mininet

```bash
sudo mn -c
```

### Step 5 — Start Controller (Terminal 1)

```bash
cd ~/pox
python3 pox.py log.level --DEBUG controller
```

### Step 6 — Start Topology (Terminal 2)

```bash
cd ~/sdn_project
sudo python3 topo.py
```
## 📸 iperf Throughput Test

### Allowed Traffic (h1 → h3)
![iperf-allowed](screenshots/iperf_allowed.png)

### Blocked Traffic (h2 → h4)
![iperf-blocked](screenshots/iperf_blocked.png)

---

## 📸 Packet Capture (tcpdump / Wireshark)

### Allowed Traffic Capture
![tcpdump-allowed](screenshots/tcpdump_allowed.png)

### Blocked Traffic Capture
![tcpdump-blocked](screenshots/tcpdump_blocked.png)
---

##  Expected Output

### Allowed Traffic

```bash
mininet> h1 ping -c 4 h3
```

✔ 0% packet loss

---

### Blocked Traffic

```bash
mininet> h2 ping -c 4 h4
```

❌ 100% packet loss

---


Expected:

* DROP rules for blocked traffic
* ALLOW rules for permitted traffic

---

## Proof of Execution


1. Controller running (POX logs)
   <img width="670" height="241" alt="image" src="https://github.com/user-attachments/assets/0b34681e-5696-4a18-9ffb-b6afc7879ac5" />

2. Mininet topology started
   <img width="649" height="698" alt="image" src="https://github.com/user-attachments/assets/503f8e29-14be-43ed-8b6e-45e023e01da5" />
<img width="593" height="197" alt="image" src="https://github.com/user-attachments/assets/21a5d4c5-7ccb-4c8c-8de8-787d44e5d246" />

3. Allowed ping (h1 → h3)
   <img width="620" height="181" alt="Screenshot 2026-04-24 002001" src="https://github.com/user-attachments/assets/84f14014-139a-4517-82ee-6d1dcb9f20d0" />

4. Blocked ping (h2 → h4)
   <img width="617" height="109" alt="Screenshot 2026-04-24 001941" src="https://github.com/user-attachments/assets/52b7e2d0-e3f5-4d16-b362-359ca7d23168" />


    
## Conclusion

This project demonstrates how SDN enables centralized control, efficient routing, and easy policy enforcement. Using POX and Mininet, static routing and firewall rules were successfully implemented, showing clear advantages over traditional networking.

---

##  References

1. OpenFlow Specification v1.0
   [https://opennetworking.org/wp-content/uploads/2013/04/openflow-spec-v1.0.0.pdf](https://opennetworking.org/wp-content/uploads/2013/04/openflow-spec-v1.0.0.pdf)

2. POX Documentation
   [https://noxrepo.github.io/pox-doc/html/](https://noxrepo.github.io/pox-doc/html/)

3. Mininet Walkthrough
   [http://mininet.org/walkthrough/](http://mininet.org/walkthrough/)

