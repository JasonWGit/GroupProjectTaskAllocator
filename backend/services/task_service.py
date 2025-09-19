from models.task import Task
from repositories.task_repo import fetch_task_from_id

def task_id_list_to_task_list(task_ids: list[str]) -> list[Task]:
    task_list: list[Task] = []
    for task_id in task_ids:
        task: Task = fetch_task_from_id(task_id)
        task_list.append(task)
    return task_list