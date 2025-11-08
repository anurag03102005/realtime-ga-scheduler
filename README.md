# Realtime_GA_Scheduler
A modular, real-time GA-based scheduler for DAG workflows (multi-VM).
This project is structured to be extended later with a DQN agent (GA-DQN hybrid).

Structure:
- ga_scheduler/: package source
    - models.py: Task and VM dataclasses
    - utils.py: DAG generation and helpers (uses networkx if available)
    - simulator.py: schedule simulator (makespan, cost)
    - ga.py: GA optimizer
    - main.py: example runner
- experiments/: notebook area for experiments
- logs/: runtime logs (for you to use)

How to run:
1. (Optional) create venv: python -m venv venv
2. pip install -r requirements.txt
3. python -m ga_scheduler.main
