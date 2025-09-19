from typing import Union

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase_client import supabase

from services.allocator import Allocator
from services.graph_service import GraphService
from repositories.worker_repo import fetch_workers
from repositories.task_repo import fetch_tasks

# this file should only interact with the service layer inside services/

app = FastAPI()
allocator = Allocator()
graph_service = GraphService()

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
    return fetch_tasks()
    # response = (
    #     supabase.table("tasks").select("*").execute()
    # )
    # return response.data

@app.get("/get_workers")
def get_workers():
    return fetch_workers()
    # response = (
    #     supabase.table("workers").select("*").execute()
    # )

    # return response.data

@app.get("/get_allocation")
def get_allocation():
    # task_and_worker_ids = None
    # try:
    #     task_and_worker_info = fetch_task_and_worker_allocation_info()
    # except HTTPException as e:
    #     raise e
    # except HTTPException as e:
    #     raise HTTPException(status_code=500, detail=str(e))

    # tasks = task_and_worker_info["tasks"]
    # workers = task_and_worker_info["workers"]
    allocation_list = allocator.do_naive_allocation()

    serialized_allocations_list = [item.to_dict() for item in allocation_list]
    return serialized_allocations_list

# @app.get("/get_allocation_formatted")
# def get_allocation_formatted():
#     allocationList = do_allocation()

#     # formattedAllocationDict = fetch_allocation_formatted(allocationDict)
#     # print(formattedAllocationDict)
#     # return formattedAllocationDict
#     return []

@app.get("/get_task_graph")
def get_task_graph():
    # return construct_graph()
    return graph_service.get_task_graph_adj_list()

@app.get("/get_topological_order")
def get_topological_order():
    # return do_topological_sort()
    return graph_service.get_task_graph_topological_sort()

@app.get("/get_graph_formatted_json")
def get_formatted_graph_json():
    # return get_graph_formatted_json()
    print(graph_service.get_task_graph_formatted_json_vis())
    return graph_service.get_task_graph_formatted_json_vis()

# @app.get("/")
# def read_root():
#     return { "data": "Hello World" }

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}