# ga_scheduler/ga.py
import random
from typing import List, Dict, Tuple
from .models import Task, VM
from .simulator import simulate_schedule

Assignment = Dict[str, Tuple[str,int]]  # task_id -> (vm_id, core_idx)

def random_assignment(tasks: List[Task], vms: Dict[str, VM]) -> Assignment:
    vm_ids = list(vms.keys())
    assgn = {}
    for t in tasks:
        vm = random.choice(vm_ids)
        core = random.randrange(vms[vm].cores)
        assgn[t.id] = (vm, core)
    return assgn

def mutate(assignment: Assignment, tasks: List[Task], vms: Dict[str, VM], mut_prob: float = 0.12) -> Assignment:
    new = assignment.copy()
    for t in tasks:
        if random.random() < mut_prob:
            vm = random.choice(list(vms.keys()))
            core = random.randrange(vms[vm].cores)
            new[t.id] = (vm, core)
    return new

def crossover(a1: Assignment, a2: Assignment, tasks: List[Task]) -> Tuple[Assignment, Assignment]:
    tids = [t.id for t in tasks]
    if len(tids) < 2:
        return a1.copy(), a2.copy()
    point = random.randrange(1, len(tids))
    c1 = {}
    c2 = {}
    for i, tid in enumerate(tids):
        if i < point:
            c1[tid] = a1[tid]
            c2[tid] = a2[tid]
        else:
            c1[tid] = a2[tid]
            c2[tid] = a1[tid]
    return c1, c2

def fitness(assignment: Assignment, tasks: List[Task], vms: Dict[str, VM],
            alpha: float = 1.0, beta: float = 1.0, gamma: float = 0.0) -> float:
    """
    Weighted fitness to minimize: alpha*makespan + beta*cost + gamma*comm
    Lower is better.
    """
    makespan, cost, comm = simulate_schedule(tasks, vms, assignment)
    return alpha*makespan + beta*cost + gamma*comm

def ga_optimize(tasks: List[Task], vms: Dict[str, VM],
                pop_size: int = 40, generations: int = 20,
                mut_prob: float = 0.12, elite_frac: float = 0.2,
                alpha: float = 1.0, beta: float = 0.3, gamma: float = 0.2,
                init_population: List[Assignment] = None) -> Tuple[Assignment, float]:
    """
    Run GA and return best assignment and its fitness value.
    Optionally pass init_population to reuse population across runs.
    """
    # initialize population
    pop = init_population if init_population else [random_assignment(tasks, vms) for _ in range(pop_size)]
    for gen in range(generations):
        scored = [(fitness(ind, tasks, vms, alpha, beta, gamma), ind) for ind in pop]
        scored.sort(key=lambda x: x[0])  # lower is better
        elites = [ind for (_, ind) in scored[:max(1, int(pop_size*elite_frac))]]
        newpop = elites.copy()
        # fill new population
        while len(newpop) < pop_size:
            # selection: pick parents from top-half (keeps pressure)
            candidates = [ind for (_, ind) in scored[:max(2, pop_size//2)]]
            p1 = random.choice(candidates)
            p2 = random.choice(candidates)
            c1, c2 = crossover(p1, p2, tasks)
            c1 = mutate(c1, tasks, vms, mut_prob)
            c2 = mutate(c2, tasks, vms, mut_prob)
            newpop.append(c1)
            if len(newpop) < pop_size:
                newpop.append(c2)
        pop = newpop
    # return best individual
    scored_final = [(fitness(ind, tasks, vms, alpha, beta, gamma), ind) for ind in pop]
    scored_final.sort(key=lambda x: x[0])
    best_f, best_ind = scored_final[0]
    return best_ind, best_f
