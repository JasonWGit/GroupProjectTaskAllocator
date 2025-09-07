from supabase_client import supabase
from typing import Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# a file for backend helper functions

class TaskData(BaseModel):
    name: str
    description: str
    duration: int
    dependencies: list[str]
    id: str

class WorkerData(BaseModel):
    id: str
    name: str

def fetch_tasks() -> TaskData:
    response = (
        supabase.table("tasks").select("*").execute()
    )
    return response.data

def fetch_workers() -> WorkerData:
    response = (
        supabase.table("workers").select("*").execute()
    )
    return response.data

# naive allocation algorithm, just allocates tasks evenly among workers. returns a
def do_allocation(tasks: list[TaskData], workers: list[WorkerData]) -> Dict[str, list[str]]:
    if len(tasks) == 0 or len(workers) == 0:
        return {}
    
    task_ids = [task["id"] for task in tasks]
    worker_ids = [worker["id"] for worker in workers]

    tasks_per_worker = len(task_ids) / len(worker_ids)

    num_tasks = 0
    allocationDict = {}

    for worker in worker_ids:
        curr_worker_tasks = []
        num_tasks = 0
        while num_tasks < tasks_per_worker:
            if len(task_ids) != 0:
                curr_worker_tasks.append(task_ids[0])
                task_ids.pop(0)
            num_tasks += 1
        allocationDict[worker] = curr_worker_tasks
    
    return allocationDict

def fetch_task_and_worker_allocation_info():
    try:
        tasks = fetch_tasks()
        workers = fetch_workers()
    except HTTPException as e:
        raise e
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=str(e))
    # task_ids = [task["id"] for task in tasks]
    # worker_ids = [worker["id"] for worker in workers]
    return {
        "tasks": tasks,
        "workers": workers
    }

def fetch_task_from_id(task_id: str):
    response = (
        supabase.table("tasks").select("*").eq("id", task_id).execute()
    )

    # since select returns a list of rows, return the first one (if a matched row exists)
    return response.data[0] if response.data else None

def fetch_worker_from_id(worker_id: str):
    response = (
        supabase.table("workers").select("*").eq("id", worker_id).execute()
    )

    # since select returns a list of rows, return the first one (if a matched row exists)
    return response.data[0] if response.data else None

# get the allocation data except it has names, duration, dependencies
def fetch_allocation_formatted(allocationDict):
    formattedAllocationDict = {}
    for worker_id, task_ids in allocationDict.items():
        worker_name = fetch_worker_from_id(worker_id)["name"]
        task_names = []
        for task_id in task_ids:
            task_name = fetch_task_from_id(task_id)["name"]

            if task_name is not None:
                task_names.append(task_name)

        formattedAllocationDict[worker_name] = task_names
    
    return formattedAllocationDict
    
        
        