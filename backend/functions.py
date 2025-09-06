from supabase_client import supabase
from typing import Dict
from fastapi import FastAPI, HTTPException

# a file for backend helper functions

# naive allocation algorithm, just allocates tasks evenly among workers
def fetch_tasks():
    response = (
        supabase.table("tasks").select("*").execute()
    )
    return response.data

def fetch_workers():
    response = (
        supabase.table("workers").select("*").execute()
    )
    return response.data

def do_allocation(task_ids: list[str], worker_ids: list[str]) -> Dict[str, list[str]]:
    if len(task_ids) == 0 or len(worker_ids) == 0:
        return {}
    
    tasks_per_worker = len(task_ids) / len(worker_ids)

    num_tasks = 0
    allocationDict = {}

    for worker in worker_ids:
        curr_worker_tasks = []
        num_tasks = 0
        while num_tasks < tasks_per_worker:
            if len(task_ids) != 0:
                curr_worker_tasks.append(task_ids[0])
                task_ids.pop()
            num_tasks += 1
        allocationDict[worker] = curr_worker_tasks
    
    return allocationDict
        






    