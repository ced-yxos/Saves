from fastapi import FastAPI
import sys
import subprocess
import uvicorn

app = FastAPI()

def cluster_status():
    # Function returning resources usage on current kubernetes cluster
    node_info = {}
    total_percent_cpu_req = 0
    total_percent_mem_req = 0
    total_percent_cpu_lim = 0
    total_percent_mem_lim = 0
    total_percent_cpu_usage = 0
    total_percent_mem_usage = 0
    init_tab_position = int(subprocess.getoutput("kubectl get nodes | awk '{print $1}' | grep -v NAME | awk '{ print length }' | sort -n | tail -1")) + 5
    tab_width = 10
    terminal_width = int(subprocess.getoutput("stty size | awk '{print $2}'"))
    set_tab_stops(init_tab_position, tab_width, terminal_width)

    if len(sys.argv) == 1:
        nodes = subprocess.getoutput("kubectl get nodes --no-headers -o custom-columns=NAME:.metadata.name").split()
    elif sys.argv[1] == "--nodes":
        nodes = sys.argv[2:]
    elif sys.argv[1] == "--pool":
        nodes = subprocess.getoutput("kubectl get nodes --no-headers -o custom-columns=NAME:.metadata.name | grep '{}'".format(sys.argv[2])).split()
    else:
        print("Wrong arg!")
        exit(1)

    print("NODE\t CPU_allocatable\t Memory_allocatable\t CPU_request%\t Memory_request%\t CPU_limit%\t Memory_limit%\t CPU_usage%\t Memory_usage%")
    i = 0
    for node in nodes:
        node_info[node] = {}
        requests = subprocess.getoutput("kubectl describe node {} | grep -A2 -E 'Resource' | tail -n1 | tr -d '(%)\n'".format(node)).split()
        abs_cpu = int(requests[1].rstrip('m'))
        percent_cpu_req = int(requests[2])
        node_cpu_req = int(abs_cpu / percent_cpu_req * 100)
        allocatable_cpu = int(node_cpu_req - abs_cpu)
        percent_cpu_lim = int(requests[4])
        requests = subprocess.getoutput("kubectl describe node {} | grep -A3 -E 'Resource' | tail -n1 | tr -d '(%)\n'".format(node)).split()
        abs_mem = int(requests[1].rstrip('Mi'))
        percent_mem_req = int(requests[2])
        node_mem_req = int(abs_mem / percent_mem_req * 100)
        allocatable_mem = int(node_mem_req - abs_mem)
        percent_mem_lim = int(requests[4])
        percent_cpu_usage = int(subprocess.getoutput("kubectl top nodes | grep {} | awk '{{print $3}}' | rev | cut -c2- | rev".format(node)))
        percent_mem_usage = int(subprocess.getoutput("kubectl top nodes | grep {} | awk '{{print $5}}' | rev | cut -c2- | rev".format(node)))
        print(f"{node}\t {allocatable_cpu}m\t\t {allocatable_mem}Ki\t\t {percent_cpu_req}%\t\t {percent_mem_req}%\t\t {percent_cpu_lim}%\t\t {percent_mem_lim}%\t\t {percent_cpu_usage}%\t\t {percent_mem_usage}%")


        node_info[node]['CPU_allocatable'] = allocatable_cpu
        node_info[node]['Memory_allocatable'] = allocatable_mem
        node_info[node]['CPU_request%'] = percent_cpu_req
        node_info[node]['Memory_request%'] = percent_mem_req
        node_info[node]['CPU_limit%'] = percent_cpu_lim
        node_info[node]['Memory_limit%'] = percent_mem_lim
        node_info[node]['CPU_usage%'] = percent_cpu_usage
        node_info[node]['Memory_usage%'] = percent_mem_usage

        if i == 0:
            i+=1
            continue
        total_percent_cpu_req += percent_cpu_req
        total_percent_mem_req += percent_mem_req
        total_percent_cpu_lim += percent_cpu_lim
        total_percent_mem_lim += percent_mem_lim
        total_percent_cpu_usage += percent_cpu_usage
        total_percent_mem_usage += percent_mem_usage

    node_count = len(nodes) - 1
    avg_percent_cpu_req = total_percent_cpu_req // node_count
    avg_percent_mem_req = total_percent_mem_req // node_count
    avg_percent_cpu_lim = total_percent_cpu_lim // node_count
    avg_percent_mem_lim = total_percent_mem_lim // node_count
    avg_percent_cpu_usage = total_percent_cpu_usage // node_count
    avg_percent_mem_usage = total_percent_mem_usage // node_count

    print("")
    print(f"Average requests: {avg_percent_cpu_req}% CPU, {avg_percent_mem_req}% memory.")
    print(f"Average limits: {avg_percent_cpu_lim}% CPU, {avg_percent_mem_lim}% memory.")
    print(f"Average usage: {avg_percent_cpu_usage}% CPU, {avg_percent_mem_usage}% memory.")

    return node_info

def set_tab_stops(init_tab_position, tab_width, terminal_width):
    tab_stops = ''
    for i in range(init_tab_position, terminal_width, tab_width):
        tab_stops += str(i) + ','
    tabs(tab_stops)

def tabs(tab_stops):
    subprocess.run(["tabs"] + tab_stops.split(','))


@app.get("/ressources")
async def ressource():
    return cluster_status()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9001)
    print("server running")
