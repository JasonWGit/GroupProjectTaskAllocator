from typing import Union

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase_client import supabase
from functions import fetch_tasks, fetch_workers, do_allocation, fetch_task_and_worker_allocation_info, fetch_allocation_formatted
from graph import construct_graph, do_topological_sort

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

class TaskInput(BaseModel):
    name: str
    description: str
    duration: str
    dependencies: list[str]

class WorkerInput(BaseModel):
    name: str

@app.post("/create_task")
def create_task(task: TaskInput):
    print(task)
    response = (
        supabase.table("tasks").insert({"name": task.name, "description": task.description, "duration": int(task.duration), "dependencies": task.dependencies }).execute()
    )
    print(f'returned response: {response}')
    return {}

@app.post("/create_worker")
def create_worker(worker: WorkerInput):
    print(worker)
    response = (
        supabase.table("workers").insert({ "name": worker.name }).execute()
    )
    print(f'returned response: {response}')
    return {}

@app.get("/get_tasks")
def get_tasks():
    response = (
        supabase.table("tasks").select("*").execute()
    )
    return response.data

@app.get("/get_workers")
def get_workers():
    response = (
        supabase.table("workers").select("*").execute()
    )

    return response.data

@app.get("/get_allocation")
def get_allocation():
    #TODO
    task_and_worker_ids = None
    try:
        task_and_worker_info = fetch_task_and_worker_allocation_info()
    except HTTPException as e:
        raise e
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=str(e))

    tasks = task_and_worker_info["tasks"]
    workers = task_and_worker_info["workers"]

    allocationDict = do_allocation(tasks, workers)
    return allocationDict

@app.get("/get_allocation_formatted")
def get_allocation_formatted():
    task_and_worker_ids = None
    try:
        task_and_worker_info = fetch_task_and_worker_allocation_info()
    except HTTPException as e:
        raise e
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=str(e))

    tasks = task_and_worker_info["tasks"]
    workers = task_and_worker_info["workers"]

    allocationDict = do_allocation(tasks, workers)

    formattedAllocationDict = fetch_allocation_formatted(allocationDict)
    print(formattedAllocationDict)
    return formattedAllocationDict

@app.get("/get_task_graph")
def get_task_graph():
    return construct_graph()

@app.get("/get_topological_order")
def get_topological_order():
    return do_topological_sort()

# @app.get("/")
# def read_root():
#     return { "data": "Hello World" }

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}