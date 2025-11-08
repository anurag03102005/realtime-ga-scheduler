# ga_scheduler/utils.py
"""Utilities: DAG generation (NetworkX), topological helpers, simple workload generator."""
from typing import List, Tuple
import random
from .models import Task

try:
    import networkx as nx
except Exception:
    nx = None

def random_dag_simple(num_tasks:int, max_preds:int=2, min_comp:float=20, max_comp:float=200):
    """Simple random DAG generator without networkx (safe fallback)."""
    tasks = []
    ids = [f"T{i+1}" for i in range(num_tasks)]
    for i, tid in enumerate(ids):
        preds = []
        if i>0:
            k = random.randint(0, min(max_preds, i))
            preds = random.sample(ids[:i], k)
        comp = random.uniform(min_comp, max_comp)
        data_size = random.uniform(0, 20)
        ttype = random.choice(["compute","io"])
        tasks.append(Task(id=tid, comp=comp, preds=preds, data_size=data_size, ttype=ttype))
    return tasks

def generate_random_workflow(num_tasks: int = 8,
                             edge_prob: float = 0.2,
                             min_comp: float = 50,
                             max_comp: float = 300) -> Tuple[object, List[Task]]:
    """
    Generate a random DAG workflow using NetworkX if available; otherwise uses simple generator.
    Returns (graph_or_None, task_list)
    """
    if nx is None:
        # fallback to simple generator (ensures environment without networkx still works)
        tasks = random_dag_simple(num_tasks, max_preds=2, min_comp=min_comp, max_comp=max_comp)
        return None, tasks

    g = nx.DiGraph()
    # Add nodes
    for i in range(num_tasks):
        g.add_node(f"T{i+1}")
    # Randomly add edges (from lower index to higher) to maintain acyclicity
    for i in range(num_tasks):
        for j in range(i+1, num_tasks):
            if random.random() < edge_prob:
                g.add_edge(f"T{i+1}", f"T{j+1}")
    # If not a DAG, retry (rare)
    if not nx.is_directed_acyclic_graph(g):
        return generate_random_workflow(num_tasks, edge_prob, min_comp, max_comp)

    tasks = []
    for node in g.nodes:
        preds = list(g.predecessors(node))
        comp = random.uniform(min_comp, max_comp)
        data_size = random.uniform(1, 20)
        ttype = random.choice(["compute","io"])
        tasks.append(Task(id=node, comp=comp, preds=preds, data_size=data_size, ttype=ttype))
    return g, tasks

def topo_order_from_tasks(tasks: List[Task]) -> List[str]:
    """Return a topological order (simple Kahn) from task list."""
    indeg = {t.id:0 for t in tasks}
    graph = {t.id:[] for t in tasks}
    for t in tasks:
        for p in t.preds:
            graph[p].append(t.id)
            indeg[t.id] += 1
    q = [tid for tid,d in indeg.items() if d==0]
    order = []
    while q:
        u = q.pop(0)
        order.append(u)
        for v in graph.get(u, []):
            indeg[v] -= 1
            if indeg[v]==0:
                q.append(v)
    if len(order) != len(tasks):
        raise ValueError("Cycle detected in DAG")
    return order
