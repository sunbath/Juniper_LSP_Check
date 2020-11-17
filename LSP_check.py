from pprint import pprint
from tabulate import tabulate

def print_table(table,headers):
    print(tabulate(table, headers, tablefmt="fancy_grid"))
    print("\n")

def junos_lsp_reader(filename):
    f = open(filename,'r')

    output = []

    for line in f.readlines():
        # Make up a list of string by splitting with " "
        line = line.split(" ")

        # Remove empty entries
        line = list(filter(lambda x: x != "", line))

        # Remove \n from the last element
        line[-1] = line[-1].strip()

        if line != ['']:
            output.append(line)

    #hostname = output[0][0].split("@")[1].strip(">")

    ingress_header_pos = [i for i,x in enumerate(output) if x[0] == "Ingress"][0]
    egress_header_pos = [i for i,x in enumerate(output) if x[0] == "Egress"][0]
    transit_header_pos = [i for i,x in enumerate(output) if x[0] == "Transit"][0]
    totals_header_pos = [i for i,x in enumerate(output) if x[0] == "Total"]

    #print(ingress_header_pos)
    #print(egress_header_pos)
    #print(transit_header_pos)
    #print(totals_header_pos)

    ingress_lsp_dict = {}
    egress_lsp_dict = {}
    transit_lsp_dict = {}

    number_of_ingress_lsp = 0
    number_of_egress_lsp = 0
    number_of_transit_lsp = 0

    for line in output[ingress_header_pos+2:ingress_header_pos+2+totals_header_pos[0]-3]:
        #print(line)
        number_of_ingress_lsp += 1
        ingress_lsp_dict.setdefault(line[-1],line[2])

    for line in output[egress_header_pos+2:egress_header_pos+2+(totals_header_pos[1]-totals_header_pos[0]-3)]:
        #print(line)
        number_of_egress_lsp += 1
        egress_lsp_dict.setdefault(line[-1],line[2])

    for line in output[transit_header_pos+2:transit_header_pos+2+(totals_header_pos[2]-totals_header_pos[1]-3)]:
        #print(line)
        number_of_transit_lsp += 1
        transit_lsp_dict.setdefault(line[-1],line[2])

    return [number_of_ingress_lsp, number_of_egress_lsp, number_of_egress_lsp], [ingress_lsp_dict, egress_lsp_dict, transit_lsp_dict]

def LSP_stat_check(hostname, pre_rollout_lsp_stat, post_rollout_lsp_stat):
    print("LSP Statistics")
    print('=' * 70)
    table = [["Ingress LSPs",pre_rollout_lsp_stat[0],post_rollout_lsp_stat[0]],["Egress LSPs",pre_rollout_lsp_stat[1],post_rollout_lsp_stat[1]],["Transit LSPs",pre_rollout_lsp_stat[2],post_rollout_lsp_stat[2]]]
    headers = [hostname,"Pre-Rollout", "Post-Rollout"]
    print_table(table,headers)

def LSP_name_comparison(LSP_type,pre_rollout_lsp_names,post_rollout_lsp_names):
    table = []
    headers = [f"{LSP_type} LSP Comparison"]
    print(f"{LSP_type} LSP Comparison")
    diff1 = pre_rollout_lsp_names - post_rollout_lsp_names
    diff2 = post_rollout_lsp_names - pre_rollout_lsp_names
    if len(diff1)>0:
        for lsp in (diff1):
            table.append([f"- {lsp}"])
    else:
        table.append([f"- 0"])
    if len(diff2)>0:
        for lsp in (diff2):
            table.append([f"+ {lsp}"])
    else:
        table.append([f"+ 0"])
    print_table(table,headers)

def LSP_definition_check(pre_rollout_status,post_rollout_status):
    # Check if LSPs are added or removed before and after rollout

    # Extract the LSP names and place them into 3 tuples: ingress, egress, transit
    pre_rollout_lsp_names = [set(pre_rollout_status[0].keys()), set(pre_rollout_status[1].keys()), set(pre_rollout_status[2].keys())]
    post_rollout_lsp_names = [set(post_rollout_status[0].keys()), set(post_rollout_status[1].keys()), set(post_rollout_status[2].keys())]

    print("LSP Definition Check")
    print('=' * 70)

    LSP_name_comparison("Ingress",pre_rollout_lsp_names[0],post_rollout_lsp_names[0])
    LSP_name_comparison("Egress",pre_rollout_lsp_names[1],post_rollout_lsp_names[1])
    LSP_name_comparison("Transit",pre_rollout_lsp_names[2],post_rollout_lsp_names[2])

def LSP_status_comparison(LSP_type,pre_rollout_status,post_rollout_status):

    # This dict is to merge the pre-rollout and post-rollout status together, because LSP may be added or removed after rollout.
    # The value is updated with the post-rollout LSP status to ensure it contains all the LSPs.
    LSP_status_dict = {**pre_rollout_status, **post_rollout_status}

    # This dict is to store those LSP whose:
    # 1. Added after rollout
    # 2. Status has been changed
    # 3. Removed after rollout
    LSP_status_change_dict = {}

    for LSP_name, LSP_status in LSP_status_dict.items():
        # Newly Defined LSPs:
        if LSP_name not in pre_rollout_status.keys():
            LSP_status_change_dict.setdefault(LSP_name,[]).append(["Not Present",LSP_status])
        # LSPs with status change
        elif LSP_status != pre_rollout_status[LSP_name]:
            LSP_status_change_dict.setdefault(LSP_name,[]).append([pre_rollout_status[LSP_name],LSP_status])
        # LSPs removed after rollout
        elif LSP_name not in post_rollout_status.keys():
            LSP_status_change_dict.setdefault(LSP_name, []).append([LSP_status,"Not Present"])

    status_change_table = []
    for LSP_name, status_change in LSP_status_change_dict.items():
        status_change_table.append([LSP_name,status_change[0][0],status_change[0][1]])
    status_change_header = [f"{LSP_type} LSP","Pre-Rollout","Post-Rollout"]
    print(tabulate(status_change_table, status_change_header, tablefmt="fancy_grid"))

def LSP_status_check(pre_rollout_status, post_rollout_status):
    print("LSP Status Check")
    print('=' * 70)

    LSP_status_comparison("Ingress",pre_rollout_status[0],post_rollout_status[0])
    LSP_status_comparison("Egress", pre_rollout_status[1], post_rollout_status[1])
    LSP_status_comparison("Transit", pre_rollout_status[2], post_rollout_status[2])

def main():

    GWAN_Routers = ['LO11']

    for hostname in GWAN_Routers:
        print("\n")
        print(f"Hostname: {hostname}")
        print("\n")
        pre_rollout_filename = hostname + "_Pre_Rollout_LSP.txt"
        post_rollout_filename = hostname + "_Post_Rollout_LSP.txt"

        pre_rollout_lsp_stat, pre_rollout_status = junos_lsp_reader(pre_rollout_filename)
        post_rollout_lsp_stat, post_rollout_status = junos_lsp_reader(post_rollout_filename)

        # Check the quantity of LSPs
        LSP_stat_check(hostname, pre_rollout_lsp_stat, post_rollout_lsp_stat)

        # Check the definition of LSPs
        LSP_definition_check(pre_rollout_status, post_rollout_status)

        # Check the status of LSPs
        LSP_status_check(pre_rollout_status, post_rollout_status)

if __name__ == '__main__':
    main()
