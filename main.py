# NITRO API Automation Use Case 1

import os
import requests

# Utilizes Simple Python Library to control Citrix Netscaler 9.2+ load balancers with NITRO API
# https://github.com/ndenev/nsnitro
from nsnitro import NSNitro, NSConfig, NSServer, NSLBVServer, NSServiceGroup, NSServiceGroupServerBinding, NSLBVServerServiceGroupBinding, NSLBMonitorServiceBinding

# Global Nitro instance    
g_nitro = NSNitro('172.16.100.200', 'nsroot', 'nsroot')
g_jira_base_url = "http://172.16.100.205:8080"
g_jira_service_account_username = "jenkins"
g_jira_service_account_password = "qRRXeefBvt"

def main():
    env_issue_id = os.getenv('ISSUE_ID')
    if not env_issue_id:
        print "Missing ISSUE_ID environment variable"
        print "exiting..."
        exit()
    request = LBvServerRequest(env_issue_id)
    # 0) Login to NetScaler
    init_nitro()
    save_nitro()
    # TODO: add other persistence types
    # 1) Create LB vServer
    create_virtual_server(
        request.vserver_name,
        request.vserver_ip_address,
        request.vserver_port,
        request.vserver_clttimeout,
        request.vserver_persistence_type,
        request.vserver_service_type
    )
    # 2) Create Service Group
    create_service_group(request.service_group_name, request.service_group_service_type)
    # 3) Bind Backend Servers to Service Group
    create_server(request.backend_server_name, request.backend_server_ip)
    bind_service_group_to_server(
        request.service_group_name,
        request.backend_server_name,
        request.service_group_binding_port,
        request.service_group_binding_weight
    )
    # 4) Binding a monitor to Service Group
    bind_monitor_to_service_group(
        request.monitor_name,
        request.service_group_name
    )
    # 5) Binding Service Group to LB vServer
    bind_service_group_to_virtual_server("test-sgroup", "test-vserver")
    save_nitro()
    notify_jira_of_creation(env_issue_id)

def init_nitro():
    global g_nitro
    try:
        g_nitro.login()
        print "Login successful"
    except Exception as e:
        print e
        print "exiting..."
        exit()

def save_nitro():
    global g_nitro
    try:
        NSConfig().save(g_nitro)
        print "Saved configuration"
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

def notify_jira_of_creation(issue_key):
    global g_jira_base_url, g_jira_service_account_username, g_jira_service_account_password
    headers = {'Content-type': 'application/json'}
    r = requests.post(
        g_jira_base_url + "/rest/api/2/issue/%s/transitions" % issue_key,
        auth = (g_jira_service_account_username, g_jira_service_account_password),
        json = {
            "transition": {
                "id": "61"
            }
        },
        headers = headers
    )
    if r.status_code == 204:
        print "Changed Jira issue status to Complete"
    else:
        print "Error changing Jira issue status"

class LBvServerRequest:
    def __init__(self, issue_key):
        try:
            global g_jira_base_url, g_jira_service_account_username, g_jira_service_account_password
            self.issue_json = requests.get(
                g_jira_base_url + "/rest/api/2/issue/%s" % issue_key,
                auth = (g_jira_service_account_username, g_jira_service_account_password)
            ).json()
            self.vserver_name = self.issue_json["fields"]["customfield_10200"]
            self.vserver_ip_address = self.issue_json["fields"]["customfield_10201"]
            self.vserver_port = int(self.issue_json["fields"]["customfield_10202"])
            self.vserver_clttimeout = int(self.issue_json["fields"]["customfield_10203"])
            self.vserver_persistence_type = self.issue_json["fields"]["customfield_10204"]["value"]
            self.vserver_service_type = self.issue_json["fields"]["customfield_10205"]["value"]
            self.service_group_name = self.issue_json["fields"]["customfield_10206"]
            self.service_group_service_type = self.issue_json["fields"]["customfield_10207"]["value"]
            self.backend_server_name = self.issue_json["fields"]["customfield_10208"]
            self.backend_server_ip = self.issue_json["fields"]["customfield_10209"]
            self.service_group_binding_port = int(self.issue_json["fields"]["customfield_10211"])
            self.service_group_binding_weight = int(self.issue_json["fields"]["customfield_10212"])
            self.monitor_name = self.issue_json["fields"]["customfield_10214"]["value"]
        except:
            print "Could not retrieve issue from Jira"
            print "exiting..."
            exit()
            

if __name__ == "__main__":
    main()
