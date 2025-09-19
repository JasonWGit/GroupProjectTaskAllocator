from pydantic import BaseModel
from functions import TaskData, WorkerData, fetch_workers
from graph import do_topological_sort

class AllocationItem():
    worker: WorkerData
    tasks: list[TaskData]

AllocationList = list[AllocationItem]
# naive allocation algorithm, just allocates tasks evenly among workers. returns a
def do_allocation() -> AllocationList:
    tasks: list[TaskData] = do_topological_sort()
    workers: list[WorkerData] = fetch_workers()

    if len(tasks) == 0 or len(workers) == 0:
        return {}

    tasks_per_worker = len(tasks) / len(workers)

    num_tasks = 0
    allocationList: AllocationList = []

    for worker in workers:
        curr_worker_tasks: list[TaskData] = []
        num_tasks = 0
        while num_tasks < tasks_per_worker:
            if len(tasks) != 0:
                curr_worker_tasks.append(tasks[0])
                tasks.pop(0)
            num_tasks += 1
        
        newAllocationItem: AllocationItem = AllocationItem(worker =  worker, tasks = curr_worker_tasks)
        allocationList.append(newAllocationItem)

    return allocationList

