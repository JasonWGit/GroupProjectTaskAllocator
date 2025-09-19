from pydantic import BaseModel
from models.task_graph.task_graph_node import TaskGraphNode
from models.task_graph.task_graph_edge import TaskGraphEdge
from models.task import Task
from dataclasses import dataclass
from interfaces.serializable import Serializable

AdjacencyList = dict[str, set[str]]

@dataclass
class GraphJSONFormatted(Serializable):
    nodes: list[TaskGraphNode]
    edges: list[TaskGraphEdge]

    def to_dict(self) -> dict:
        nodes_dict_list: list[dict] = [node.to_dict() for node in self.nodes]
        edges_dict_list: list[dict] = [edge.to_dict() for edge in self.edges]

        return {
            "nodes": nodes_dict_list,
            "edges": edges_dict_list
        }

class TaskGraph:
    def __init__(self, tasks: list[Task]):
        self.adjacency_list = None
        
        adjacencyList: AdjacencyList = {}
        
        for task in tasks:
            adjacencyList[task.id] = set()
        # TODO: add cycle detection!
        # also check if a task depends on a task that doesn't exist

        for task in tasks:
            print(task)
            for dependency in task.dependencies:
                adjacencyList[dependency].add(task.id)
        
        self.adjacency_list = adjacencyList
        self.tasks = tasks

    # performs topological sort 
    # returns list of task ids in topological order
    def topological_sort(self) -> list[Task]:
        in_degrees = {u: 0 for u in self.adjacency_list}
        for u in self.adjacency_list:
            for v in self.adjacency_list[u]:
                in_degrees[v] = in_degrees.get(v, 0) + 1
        
        S = {u for u in in_degrees if in_degrees[u] == 0}
    
        topological_order: list[str] = []

        while S:
            u = S.pop()
            topological_order.append(u)

            # remove all outgoing edges (u -> v)
            for v in list(self.adjacency_list.get(u, [])):
                in_degrees[v] -= 1
                if in_degrees[v] == 0:
                    S.add(v)

        topological_order_tasks = []
        ids_task_dict = self.get_graph_ids_to_tasks_mapping()

        for task_id in topological_order:
            topological_order_tasks.append(ids_task_dict[task_id])
        return topological_order_tasks

    # function which convert adjacency list into a JSON form understandable by frontend vis.js
    def get_graph_formatted_json(self) -> GraphJSONFormatted:
        formatted_nodes_list: list[TaskGraphNode] = []
        formatted_edges_list: list[TaskGraphEdge] = []
        id_task_dict = self.get_graph_ids_to_tasks_mapping()
        for task in id_task_dict.values():
            formatted_nodes_list.append(TaskGraphNode(id = task.id, label=task.name))
            for dependent_node_id in task.dependencies:
                formatted_edges_list.append(TaskGraphEdge(from_id = dependent_node_id, to_id = task.id))
        
        return GraphJSONFormatted(nodes = formatted_nodes_list, edges = formatted_edges_list)

    # function which returns a mapping between task ids and task objects
    def get_graph_ids_to_tasks_mapping(self) -> dict[str, Task]:
        id_to_task_dict: dict[str, Task] = {}
        for task in self.tasks:
            id_to_task_dict[task.id] = task
        
        return id_to_task_dict
    
    

