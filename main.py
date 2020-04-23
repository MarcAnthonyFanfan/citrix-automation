# NITRO API Automation Use Case 1

# Utilizes Simple Python Library to control Citrix Netscaler 9.2+ load balancers with NITRO API
# https://github.com/ndenev/nsnitro
from nsnitro import NSNitro, NSServer, NSLBVServer, NSServiceGroup, NSServiceGroupServerBinding, NSLBVServerServiceGroupBinding, NSLBMonitorServiceBinding

# Global Nitro instance
g_nitro = NSNitro('172.16.100.200', 'nsroot', 'nsroot')

def main():
    # 0) Login to NetScaler
    init_nitro()
    # TODO: add a config save at the beginning
    # 1) Create LB vServer
    create_virtual_server("test-vserver", "99.99.99.2", 5000, 180, "NONE", "HTTP")
    # 2) Create Service Group
    create_service_group("test-sgroup", "HTTP")
    # 3) Bind Backend Servers to Service Group
    create_server("test-server", "99.99.99.1")
    bind_service_group_to_server("test-sgroup", "test-server", 80, 1)
    # 4) Binding a monitor to Service Group
    bind_monitor_to_service_group("http", "test-sgroup")
    # 5) Binding Service Group to LB vServer
    bind_service_group_to_virtual_server("test-sgroup", "test-vserver")
    # TODO: add a config save at the end

def init_nitro():
    global g_nitro
    try:
        g_nitro.login()
        print "Login Successful"
    except Exception as e:
        print e
        print "exiting..."
        exit()

def create_server(name, ip):
    global g_nitro
    try:
        new_server = NSServer()
        new_server.set_name(name)
        new_server.set_ipaddress(ip)
        NSServer.add(g_nitro, new_server)
        print "Created new server: %s %s" % (name, ip)
    except Exception as e:
        print e

def create_virtual_server(name, ip, port, clttimeout, persistencetype, servicetype):
    global g_nitro
    try:
        new_virtual_server = NSLBVServer()
        new_virtual_server.set_name(name)
        new_virtual_server.set_ipv46(ip)
        new_virtual_server.set_port(port)
        new_virtual_server.set_clttimeout(clttimeout)
        new_virtual_server.set_persistencetype(persistencetype)
        new_virtual_server.set_servicetype(servicetype)
        NSLBVServer.add(g_nitro, new_virtual_server)
        print "Created new virtual server: %s %s:%d" % (name, ip, port)
    except Exception as e:
        print e

def create_service_group(name, servicetype):
    global g_nitro
    try:
        new_service_group = NSServiceGroup()
        new_service_group.set_servicegroupname(name)
        new_service_group.set_servicetype(servicetype)
        NSServiceGroup.add(g_nitro, new_service_group)
        print "Created new service group: %s %s" % (name, servicetype)
    except Exception as e:
        print e

def bind_service_group_to_server(service_group_name, server_name, port, weight):
    global g_nitro
    try:
        new_service_group_binding = NSServiceGroupServerBinding()
        new_service_group_binding.set_servicegroupname(service_group_name)
        new_service_group_binding.set_servername(server_name)
        new_service_group_binding.set_port(port)
        new_service_group_binding.set_weight(weight)
        NSServiceGroupServerBinding.add(g_nitro, new_service_group_binding)
        print "Bound service group: %s to server: %s" % (service_group_name, server_name)
    except Exception as e:
        print e

def bind_service_group_to_virtual_server(service_group_name, virtual_server_name):
    global g_nitro
    try:
        new_service_group_binding = NSLBVServerServiceGroupBinding()
        new_service_group_binding.set_servicegroupname(service_group_name)
        new_service_group_binding.set_name(virtual_server_name)
        NSLBVServerServiceGroupBinding.add(g_nitro, new_service_group_binding)
        print "Bound service group: %s to virtual server: %s" % (service_group_name, virtual_server_name)
    except Exception as e:
        print e

def bind_monitor_to_service_group(monitor_name, service_group_name):
    global g_nitro
    try:
        new_monitor_binding = NSLBMonitorServiceBinding()
        new_monitor_binding.set_servicegroupname(service_group_name)
        new_monitor_binding.set_monitorname(monitor_name)
        NSLBMonitorServiceBinding.add(g_nitro, new_monitor_binding)
        print "Bound monitor: %s to service group: %s" % (monitor_name, service_group_name)
    except Exception as e:
        print e

if __name__ == "__main__":
    main()
