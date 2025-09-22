from models.task import Task
from repositories.task_repo import fetch_task_from_id, fetch_tasks

def task_id_list_to_task_list(task_ids: list[str]) -> list[Task]:
    task_list: list[Task] = []
    for task_id in task_ids:
        task: Task = fetch_task_from_id(task_id)
        task_list.append(task)
    return task_list

def get_task_id_to_task_dict() -> dict[str, Task]:
    '''
    returns dictionary mapping task id to Task object, for fast access purposes within algorithm
    '''
    tasks = fetch_tasks()
    task_id_to_task_dict: dict[str, Task] = {}
    for task in tasks:
        task_id_to_task_dict[task.id] = task
    
    return task_id_to_task_dict