# ga_scheduler/main.py
from .models import Task, VM
from .utils import generate_random_workflow
from .ga import ga_optimize
from .simulator import simulate_schedule

def build_example():
    tasks_viz, tasks = generate_random_workflow(num_tasks=6, edge_prob=0.35)
    vms = {
        'VM1': VM('VM1', speeds=500.0, cores=2, cost_rate=1.0, vtype='mem', current_wait=0.1),
        'VM2': VM('VM2', speeds=250.0, cores=2, cost_rate=0.6, vtype='stor', current_wait=0.5),
        'VM3': VM('VM3', speeds=400.0, cores=1, cost_rate=1.2, vtype='mem', current_wait=0.0)
    }
    return tasks_viz, tasks, vms

def run_example():
    g, tasks, vms = None, None, None
    g, tasks, vms = None, None, None
    g, tasks = generate_random_workflow(num_tasks=6, edge_prob=0.35)
    tasks_list = tasks
    vms_dict = {
        'VM1': VM('VM1', speeds=500.0, cores=2, cost_rate=1.0, vtype='mem', current_wait=0.1),
        'VM2': VM('VM2', speeds=250.0, cores=2, cost_rate=0.6, vtype='stor', current_wait=0.5),
        'VM3': VM('VM3', speeds=400.0, cores=1, cost_rate=1.2, vtype='mem', current_wait=0.0)
    }
    best_assign, score = ga_optimize(tasks_list, vms_dict,
                                     pop_size=30, generations=20,
                                     mut_prob=0.15, alpha=1.0, beta=0.3, gamma=0.2)
    print("Best fitness:", score)
    print("Assignment:")
    for t in tasks_list:
        print(f"  {t.id} -> {best_assign[t.id]}")
    makespan, cost, comm = simulate_schedule(tasks_list, vms_dict, best_assign)
    print(f"Makespan: {makespan:.3f}s, Cost: {cost:.3f}, Comm: {comm:.3f}s")

if __name__ == "__main__":
    run_example()
