from typing import Union

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase_client import supabase
from functions import fetch_tasks, fetch_workers, do_allocation

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

class Task(BaseModel):
    name: str
    description: str
    duration: str
    dependencies: list[str]

class Worker(BaseModel):
    name: str

@app.post("/create_task")
def create_task(task: Task):
    print(task)
    response = (
        supabase.table("tasks").insert({"name": task.name, "description": task.description, "duration": int(task.duration), "dependencies": task.dependencies }).execute()
    )
    print(f'returned response: {response}')
    return {}

@app.post("/create_worker")
def create_worker(worker: Worker):
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
    tasks = None
    workers = None
    try:
        tasks = fetch_tasks()
        workers = fetch_workers()
    except HTTPException as e:
        raise e
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=str(e))

    task_ids = [task["id"] for task in tasks]
    worker_ids = [worker["id"] for worker in workers]

    allocationDict = do_allocation(task_ids, worker_ids)
    print(allocationDict)
    return allocationDict
    

# @app.get("/")
# def read_root():
#     return { "data": "Hello World" }

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}