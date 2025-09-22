from models.worker import Worker
from repositories.worker_repo import fetch_workers

def get_worker_id_to_worker_dict() -> dict[str, Worker]:
    '''
    returns dictionary mapping worker id to Worker object, for fast access purposes within algorithm
    '''
    workers = fetch_workers()
    worker_id_to_worker_dict: dict[str, Worker] = {}
    for worker in workers:
        worker_id_to_worker_dict[worker.id] = worker
    
    return worker_id_to_worker_dict