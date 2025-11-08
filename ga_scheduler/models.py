# ga_scheduler/models.py
"""
Core data models for the GA-based real-time scheduler.
This module defines Task and VM classes used across the project.
"""

from dataclasses import dataclass, field
from typing import List, Union

@dataclass
class Task:
    """
    Represents a node in a workflow DAG.
    Each task may depend on one or more predecessor tasks.
    """
    id: str                      # unique ID, e.g. "T1"
    comp: float                  # computation demand (in Million Instructions)
    preds: List[str] = field(default_factory=list)   # list of predecessor task IDs
    data_size: float = 0.0       # data transferred from each predecessor (MB)
    ttype: str = "compute"       # 'compute' or 'io'

    def __repr__(self):
        return f"Task({{self.id}}, comp={{self.comp:.1f}}, preds={{self.preds}})"


@dataclass
class VM:
    """
    Represents a virtual machine (VM) available for scheduling.
    """
    id: str
    speeds: Union[float, List[float]]  # MIPS per core, or single float if all cores same
    cores: int = 1
    cost_rate: float = 1.0             # cost per second
    vtype: str = "general"             # 'compute' or 'storage'
    current_wait: float = 0.0          # real-time queue waiting time (seconds)

    def core_speed(self, core_idx: int) -> float:
        """Return the MIPS speed of a given core index."""
        if isinstance(self.speeds, (list, tuple)):
            return self.speeds[core_idx % len(self.speeds)]
        return float(self.speeds)

    def __repr__(self):
        return (f"VM({{self.id}}, cores={{self.cores}}, speed={{self.speeds}}, "
                f"cost={{self.cost_rate}}, wait={{self.current_wait}})")
