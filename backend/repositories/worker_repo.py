from supabase_client import supabase
from models.worker import Worker

##### file for fetching directly from database related to workers ####

def fetch_workers() -> list[Worker]:
    response = (
        supabase.table("workers").select("*").execute()
    )

    worker_list: list[Worker] = []
    
    for worker_row in response.data:
        new_worker = Worker(
            id=worker_row['id'],
            name=worker_row['name']
        )

        worker_list.append(new_worker)
    return worker_list

def fetch_worker_from_id(worker_id: str) -> Worker:
    response = (
        supabase.table("workers").select("*").eq("id", worker_id).execute()
    )

    # since select returns a list of rows, return the first one (if a matched row exists)
    if not response.data:
        return None

    first_worker_row = response.data[0]
    
    fetched_worker = Worker(
        id=first_worker_row['id'],
        name=first_worker_row['name']
    )

    return fetched_worker