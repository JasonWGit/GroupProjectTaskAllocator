from dataclasses import dataclass
from typing import Optional

from interfaces.serializable import Serializable
from models.worker import Worker
from services.allocator import AllocationItem, Allocator
from datetime import datetime, timedelta
from services.graph_service import GraphService
import time

# arbitrary start_time for first task
ARBITRARY_START = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

@dataclass
class GanttTask(Serializable):
    id: str
    name: str
    start: str
    end: str
    progress: int # number between 0 and 100
    dependencies: Optional[str] # comma separate d list of task ids
    custom_class: Optional[str]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start": self.start,
            "end": self.end,
            "progress": self.progress,
            "dependencies": self.dependencies,
            "custom_class": self.custom_class
        }

class GanttChartService:
    def get_allocation_gantt_chart_json(self, algorithm: str):
        '''
        dispatches allocation to requested algorithm and returns the serialized gantt chart visualisation data
        '''
        allocator = Allocator()
        if algorithm == "naive":
            start = time.perf_counter()

            naive_allocation_list = allocator.do_naive_allocation()

            end = time.perf_counter()
            print(f'naive allocation took {end - start:.6f} seconds')
            return self._get_gantt_chart_json_data(naive_allocation_list)
        elif algorithm == "greedy":
            start = time.perf_counter()

            greedy_allocation_list = allocator.do_greedy_allocation()

            end = time.perf_counter()
            print(f'greedy allocation took {end - start:.6f} seconds')

            return self._get_gantt_chart_json_data(greedy_allocation_list)
        elif algorithm == "dp":
            start = time.perf_counter()

            dp_allocation_list = allocator.do_dp_allocation()

            end = time.perf_counter()
            print(f'dp allocation took {end - start:.6f} seconds')

            return self._get_gantt_chart_json_data(dp_allocation_list)
        
    def _get_gantt_chart_json_data(self, allocation_list: list[AllocationItem]):
        '''
        takes an allocation list and returns the necessary serializable structure which gets converted into valid JSON upon return by fastapi for frontend gantt chart visualisation
        '''
        # allocator_service = Allocator()
        # naive_allocation: list[AllocationItem] = allocator_service.do_naive_allocation()
        graph_service = GraphService()

        topological_ordered_tasks = graph_service.get_task_graph_topological_sort()

        # pre processing linking task_id to name of worker the task is allocated to
        task_id_to_worker_map: dict[str, Worker] = {}
        for allocation_item in allocation_list:
            for task in allocation_item.tasks:
                task_id_to_worker_map[task.id] = allocation_item.worker

        # map linking task.id to that tasks end time
        task_end_times = {}

        # dict mapping worker.id -> finish time of last task, to track when a worker becomes available again to start another task
        worker_last_task_finish: dict[str, datetime] = {a.worker.id: ARBITRARY_START for a in allocation_list}

        gantt_tasks: list[GanttTask] = []

        for task in topological_ordered_tasks:
            dep_end = max([task_end_times[dep] for dep in task.dependencies], default=ARBITRARY_START)

            # fetch the worker which is allocated to this task
            allocated_worker: Worker = task_id_to_worker_map[task.id]
            # get the time that the allocated workers last task finished (i.e. when they can potentially start this task)
            time_worker_available = worker_last_task_finish[allocated_worker.id]

            # start time for the task is either when the worker becomes available or when all the tasks dependencies are finished, whichever is greater 
            start_time = max(dep_end, time_worker_available)
            end_time = start_time + timedelta(hours=task.duration)

            # update maps
            task_end_times[task.id] = end_time
            worker_last_task_finish[allocated_worker.id] = end_time

            gantt_tasks.append(GanttTask(
                id=task.id,
                name=f"{task.name} ({task_id_to_worker_map[task.id].name}) ({task.duration} hours)",
                start=start_time.isoformat(),
                end=end_time.isoformat(),
                progress=0,
                dependencies=",".join(task.dependencies),
                custom_class=None
            ))
        
        return self._gantt_task_list_to_dict_list(gantt_tasks)
    
    def _gantt_task_list_to_dict_list(self, gantt_tasks_list: list[GanttTask]):
        '''
        converts list of gantt task to a list of the dictionary form of gantt tasks for trasnfer to frontend
        '''
        gantt_task_dict_list = [task.to_dict() for task in gantt_tasks_list]
        return gantt_task_dict_list
    







        




        
        