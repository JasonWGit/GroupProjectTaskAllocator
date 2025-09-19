from models.task_graph.task_graph import TaskGraph, AdjacencyList
from models.task import Task
from repositories.task_repo import fetch_tasks

class GraphService():
    # fetch tasks to construct an instance of TaskGraph in adj list form
    def get_task_graph_adj_list(self) -> AdjacencyList:
        graph: TaskGraph = self._create_graph()
        return graph.adjacency_list
    
    # return topological sort of task graph
    def get_task_graph_topological_sort(self) -> list[Task]:
         graph: TaskGraph = self._create_graph()
         return graph.topological_sort()

    # wrapper function to get formatted json version of graph for frontend vis.js to use
    def get_task_graph_formatted_json_vis(self):
        graph: TaskGraph = self._create_graph()
        return graph.get_graph_formatted_json().to_dict()
    
    # helper function to create graph from tasks
    def _create_graph(self) -> TaskGraph:
        tasks: list[Task] = fetch_tasks()
        graph: TaskGraph = TaskGraph(tasks)
        return graph
    