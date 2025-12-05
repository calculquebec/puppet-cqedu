#!/bin/python3

import json
import sys
from subprocess import check_output, CalledProcessError

scontrol = '/opt/software/slurm/bin/scontrol'
def get_nodes():
    try:
        controls = check_output([scontrol, '-o', 'show', 'node', '--json'], encoding='utf-8')
        output = json.loads(controls)
        return output['nodes']
    except CalledProcessError:
        return []

def get_config_value(value):
    try:
        controls = check_output([scontrol, 'show', 'config'], encoding='utf-8')
        for line in controls.split('\n'):
            if line.startswith(value):
                return line.split('=')[1].strip()
        return ""
    except CalledProcessError:
        return ""

def get_nodes_name(nodes,partition, excluded_states=['POWERED_DOWN', 'NOT_RESPONDING'], included_states=[]):
    nodes_subset = []
    for node in nodes:
        if partition in node['partitions']:
            if not any([x in node['state'] for x in excluded_states]) and ((not included_states) or any([x in node['state'] for x in included_states])):
                nodes_subset.append(node['name'])
    return list(set(nodes_subset))

def count_nodes(nodes, partition, excluded_states=['POWERED_DOWN', 'NOT_RESPONDING'], included_states=[]):
    return len(get_nodes_name(nodes, partition, excluded_states, included_states))

def count_available_nodes(nodes, partition):
    return count_nodes(nodes, partition, excluded_states=['POWERED_DOWN', 'NOT_RESPONDING', 'ALLOCATED', 'DRAIN', 'POWER_DOWN', 'DRAINED', 'DRAINING', 'FAIL', 'NO_RESPOND', 'ALLOC', 'POWERING_DOWN'])

def count_online_nodes(nodes, partition):
    return count_nodes(nodes, partition, excluded_states=['POWERED_DOWN', 'DRAIN', 'POWER_DOWN', 'DRAINED', 'DRAINING', 'FAIL', 'NO_RESPOND', 'POWERING_DOWN', 'NOT_RESPONDING'])

def count_booting_nodes(nodes, partition):
    return count_nodes(nodes, partition, excluded_states=[], included_states=['POWERING_UP'])

def count_alloc_nodes(nodes, partition):
    return count_nodes(nodes, partition, excluded_states=[], included_states=['ALLOCATED', 'ALLOC'])

def update_suspend_exc_nodes_string(suspend_exc_nodes, partition, num_target_nodes):
    lst = suspend_exc_nodes.split(',')
    if suspend_exc_nodes == "(null)":
        lst = []

    for i, item in enumerate(lst):
        if item.startswith(partition):
            lst[i] = f"{partition}[1-{num_nodes_in_partition}]:{num_target_nodes}"
            return ','.join(lst)
    # if it gets here, it was not found, add it
    lst.append(f"{partition}[1-{num_nodes_in_partition}]:{num_target_nodes}")
    return ','.join(lst)

if __name__ == "__main__":
    min_available_nodes = int(sys.argv[1])
    controlled_partitions = sys.argv[2].split(',')

    nodes = get_nodes()
    suspend_exc_nodes = get_config_value('SuspendExcNodes')

    for partition in controlled_partitions:
        num_online_nodes = count_online_nodes(nodes, partition)
        num_booting_nodes = count_booting_nodes(nodes, partition)
        num_online_or_booting_nodes = num_online_nodes + num_booting_nodes
        num_alloc_nodes = count_alloc_nodes(nodes, partition)
        num_available_nodes = num_online_or_booting_nodes - num_alloc_nodes

        num_missing_nodes = min_available_nodes - (num_online_or_booting_nodes - num_alloc_nodes)
        num_target_nodes = num_online_or_booting_nodes + num_missing_nodes
        num_nodes_in_partition = count_nodes(nodes, partition, excluded_states=[])
        if num_target_nodes > num_nodes_in_partition:
            num_target_nodes = num_nodes_in_partition
        num_missing_nodes = num_target_nodes - num_online_or_booting_nodes


        print(f"partition:{partition}, num_online_nodes:{num_online_nodes}, num_booting_nodes:{num_booting_nodes}, num_online_or_booting_nodes:{num_online_or_booting_nodes}, num_alloc_nodes:{num_alloc_nodes}, num_missing_nodes={num_missing_nodes}, num_target_nodes={num_target_nodes}, num_nodes_in_partition:{num_nodes_in_partition}")
        if num_target_nodes > num_online_or_booting_nodes:
            offline_nodes = get_nodes_name(nodes, partition, excluded_states=[], included_states=['POWERED_DOWN'])
            print(f"not enough available nodes in partition {partition}, wanting {num_target_nodes}, got {num_online_or_booting_nodes}, powering up {num_missing_nodes} nodes")
            for offline_node in offline_nodes[:num_missing_nodes]:
                print(f"powering up {offline_node}")
                controls = check_output(['sudo', scontrol, 'update', f'node={offline_node}', 'state=power_up'], encoding='utf-8')

        # if we need more or less nodes to stay on
        if num_target_nodes != num_online_or_booting_nodes:
            suspend_exc_nodes_new = update_suspend_exc_nodes_string(suspend_exc_nodes, partition, num_target_nodes)
            if suspend_exc_nodes != suspend_exc_nodes_new or suspend_exc_nodes_new != get_config_value('SuspendExcNodes'):
                print(f"updating SuspendExcNodes to {suspend_exc_nodes_new}")
                controls = check_output(['sudo', scontrol, 'update', f'SuspendExcNodes={suspend_exc_nodes_new}'])
                suspend_exc_nodes = suspend_exc_nodes_new
