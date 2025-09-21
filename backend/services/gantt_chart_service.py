from dataclasses import dataclass
from typing import Optional

from interfaces.serializable import Serializable
from services.allocator import AllocationItem, Allocator
from datetime import datetime, timedelta
from services.graph_service import GraphService

# arbitrary start_time for first task
ARBITARY_START = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

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
    def _get_gantt_chart_json_data(self, allocation_list: list[AllocationItem]):
        '''
        takes an allocation list and returns the necessary JSON data to visualise a gantt chart
        '''
        # allocator_service = Allocator()
        # naive_allocation: list[AllocationItem] = allocator_service.do_naive_allocation()
        graph_service = GraphService()

        topological_ordered_tasks = graph_service.get_task_graph_topological_sort()

        # pre processing linking task_id to name of worker the task is allocated to
        task_id_to_worker_name_map = {}
        for allocation_item in allocation_list:
            for task in allocation_item.tasks:
                task_id_to_worker_name_map[task.id] = allocation_item.worker.name

        # map linking task.id to that tasks end time
        task_end_times = {}

        gantt_tasks: list[GanttTask] = []
        project_start = ARBITARY_START

        for task in topological_ordered_tasks:
            dep_end = max([task_end_times[dep] for dep in task.dependencies], default=project_start)
            start_time = dep_end
            end_time = start_time + timedelta(hours=task.duration)

            # add this tasks end time to map of 
            task_end_times[task.id] = end_time

            gantt_tasks.append(GanttTask(
                id=task.id,
                name=f"{task.name} ({task_id_to_worker_name_map[task.id]}) ({task.duration} hours)",
                start=start_time.isoformat(),
                end=end_time.isoformat(),
                progress=0,
                dependencies=",".join(task.dependencies),
                custom_class=None
            ))
        
        return self._gantt_task_list_to_dict_list(gantt_tasks)

    def get_naive_allocation_gantt_chart_json(self):
        allocator = Allocator()
        naive_allocation_list = allocator.do_naive_allocation()
        return self._get_gantt_chart_json_data(naive_allocation_list)
    
    def _gantt_task_list_to_dict_list(self, gantt_tasks_list: list[GanttTask]):
        '''
        converts list of gantt task to a list of the dictionary form of gantt tasks for trasnfer to frontend
        '''
        gantt_task_dict_list = [task.to_dict() for task in gantt_tasks_list]
        return gantt_task_dict_list






        




        
        