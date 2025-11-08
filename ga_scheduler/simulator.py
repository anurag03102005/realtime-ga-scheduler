# ga_scheduler/simulator.py
from typing import Dict, Tuple, List
from .models import Task, VM
from .utils import topo_order_from_tasks

def simulate_schedule(tasks: List[Task],
                      vms: Dict[str, VM],
                      assignment: Dict[str, Tuple[str,int]],
                      bandwidth_mb_s: float = 100.0,
                      fixed_transfer_latency: float = 0.02) -> Tuple[float, float, float]:
    """
    Simulate schedule respecting dependencies and per-core availability.
    assignment: mapping task_id -> (vm_id, core_idx)
    Returns: (makespan_seconds, total_cost, total_comm_seconds)
    """
    id2task = {t.id: t for t in tasks}
    # initialize per-VM core free times from VM.current_wait
    core_free = {vm_id: [vm.current_wait for _ in range(vm.cores)] for vm_id, vm in vms.items()}
    finish_times = {}
    total_cost = 0.0
    # iterate in topo order
    topo = topo_order_from_tasks(tasks)
    for tid in topo:
        task = id2task[tid]
        vm_id, core_idx = assignment[tid]
        vm = vms[vm_id]
        core_speed = vm.core_speed(core_idx)
        exec_time = task.comp / core_speed
        # find predecessor finish
        pred_finish = 0.0
        comm_delay = 0.0
        for p in task.preds:
            pf = finish_times[p]
            pred_finish = max(pred_finish, pf)
            if assignment[p][0] != vm_id:
                # approximate transfer time: data_size / bandwidth + fixed latency
                comm = task.data_size / bandwidth_mb_s + fixed_transfer_latency
                comm_delay = max(comm_delay, comm)
        earliest_core = core_free[vm_id][core_idx]
        start_time = max(pred_finish + comm_delay, earliest_core)
        finish_time = start_time + exec_time
        finish_times[tid] = finish_time
        core_free[vm_id][core_idx] = finish_time
        total_cost += exec_time * vm.cost_rate
    makespan = max(finish_times.values()) if finish_times else 0.0
    # compute total communication time (sum of crossing edges)
    total_comm = 0.0
    for t in tasks:
        for p in t.preds:
            if assignment[p][0] != assignment[t.id][0]:
                total_comm += t.data_size / bandwidth_mb_s + fixed_transfer_latency
    return makespan, total_cost, total_comm
