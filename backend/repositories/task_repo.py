from models.task import Task
from repositories.worker_repo import fetch_workers
from supabase_client import supabase
from fastapi import FastAPI, HTTPException

##### file for fetching directly from database related to tasks ####

def fetch_tasks() -> list[Task]:
    response = (
        supabase.table("tasks").select("*").execute()
    )
    tasks: list[Task] = []
    for task_row in response.data:
        new_task: Task = Task(
            id=task_row['id'],              
            name=task_row['name'], 
            description=task_row['description'], 
            duration=task_row['duration'], 
            dependencies=task_row['dependencies']
        )
        tasks.append(new_task)
    return tasks

def fetch_task_from_id(task_id: str) -> Task:
    response = (
        supabase.table("tasks").select("*").eq("id", task_id).execute()
    )

    if not response.data:
        return None
    # since select returns a list of rows, return the first one (if a matched row exists)
    first_task_row = response.data[0]
    fetched_task: Task = Task(
            id=first_task_row['id'],              
            name=first_task_row['name'], 
            description=first_task_row['description'], 
            duration=first_task_row['duration'], 
            dependencies=first_task_row['dependencies']
        )
    return fetched_task

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