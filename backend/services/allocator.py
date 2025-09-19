from dataclasses import dataclass
from pydantic import BaseModel
from models.task import Task
from models.worker import Worker
from models.task_graph.task_graph import TaskGraph
from repositories.task_repo import fetch_tasks
from repositories.worker_repo import fetch_workers
from interfaces.serializable import Serializable

@dataclass
class AllocationItem(Serializable):
    worker: Worker
    tasks: list[Task]

    def to_dict(self) -> dict:
        task_dict_list: list[dict] = [task.to_dict() for task in self.tasks]
        
        return {
            "worker": self.worker,
            "tasks": task_dict_list
        }

class Allocator:
    # naive allocation algorithm, just allocates tasks evenly among workers. returns a
    def do_naive_allocation(self) -> list[AllocationItem]:
        tasks = fetch_tasks()
        workers: list[Worker] = fetch_workers()

        task_graph: TaskGraph = TaskGraph(tasks)
        topological_order_tasks = task_graph.topological_sort()
        # tasks: list[Task] = do_topological_sort()
        
        if len(topological_order_tasks) == 0 or len(workers) == 0:
            return {}

        tasks_per_worker = len(tasks) / len(workers)

        num_tasks = 0
        allocationList: list[AllocationItem] = []

        for worker in workers:
            curr_worker_tasks: list[Task] = []
            num_tasks = 0
            while num_tasks < tasks_per_worker:
                if len(tasks) != 0:
                    curr_worker_tasks.append(tasks[0])
                    tasks.pop(0)
                num_tasks += 1
            
            newAllocationItem: AllocationItem = AllocationItem(worker =  worker, tasks = curr_worker_tasks)
            allocationList.append(newAllocationItem)

        return allocationList