from functions import fetch_tasks, fetch_workers, TaskData, WorkerData, task_id_list_to_task_list
from typing import Dict, Set
from pydantic import BaseModel, Field

# file to store the graph data structure to model the task and dependencies as a DAG 
Graph = Dict[str, Set[str]]

class GraphNodeFormatted(BaseModel):
    id: str
    label: str

class GraphEdgeFormatted(BaseModel):
    from_: str = Field(..., alias="from")
    to: str

    model_config = {
        "populate_by_name": True
    }

class GraphJSONFormatted(BaseModel):
    nodes: list[GraphNodeFormatted]
    edges: list[GraphEdgeFormatted]

# function that takes a list of tasks and their dependencies and constructs a graph 
def construct_graph_from_tasks(tasks: list[TaskData]) -> Graph:
    # pre processing to make a hashmap that maps task id to the actual task object -> makes graph construction easier. Also to set up the adjacency list
    # taskDict = {}
    adjacencyList: Graph = {}
    for task in tasks: 
        # taskDict[task['id']] = task
        adjacencyList[task['id']] = set()
    
    # TODO: add cycle detection!

    for task in tasks:
        for dependency in task['dependencies']:
            adjacencyList[dependency].add(task['id'])
    
    return adjacencyList

# wrapper function to fetch tasks and input it to the above function
def construct_graph() -> Graph:
    tasks = fetch_tasks()
    return construct_graph_from_tasks(tasks)

# function that takes a graph and performs topological sort 
# returns list of task ids in topological order
def topological_sort(task_graph: Graph) -> list[str]:
    in_degrees = {u: 0 for u in task_graph}
    for u in task_graph:
       for v in task_graph[u]:
           in_degrees[v] = in_degrees.get(v, 0) + 1
    
    S = {u for u in in_degrees if in_degrees[u] == 0}
   
    topological_order: list[str] = []

    while S:
        u = S.pop()
        topological_order.append(u)

        # remove all outgoing edges (u -> v)
        for v in list(task_graph.get(u, [])):
            in_degrees[v] -= 1
            if in_degrees[v] == 0:
                S.add(v)
        
    return topological_order

# wrapper function to fetch topological order
def do_topological_sort() -> list[TaskData]:
    task_graph = construct_graph()
    topological_order_task_ids = topological_sort(task_graph)
    topological_order_tasks = task_id_list_to_task_list(task_graph)

    return topological_order_tasks

# function which convert adjacency list into a JSON form understandable by frontend vis.js
def adjacency_list_to_json_format(adj_list: Graph) -> GraphJSONFormatted:
    formatted_nodes_list: list[GraphNodeFormatted] = []
    formatted_edges_list: list[GraphEdgeFormatted] = []
    id_task_dict = get_ids_to_task_mapping()
    for taskData in id_task_dict.values():
        formatted_nodes_list.append(GraphNodeFormatted(id = taskData['id'], label=taskData['name']))
        for dependent_node_id in taskData['dependencies']:
            formatted_edges_list.append(GraphEdgeFormatted(from_ = dependent_node_id, to = taskData['id']))
    
    return GraphJSONFormatted(nodes = formatted_nodes_list, edges = formatted_edges_list)

# wrapper function to get formatted json version of graph for frontend vis.js to use
def get_graph_formatted_json():
    adj_list_graph = construct_graph()
    return adjacency_list_to_json_format(adj_list_graph)
    
# returns a dictionary mapping ids to tasks -> pre processing for other functions
def get_ids_to_task_mapping() -> dict[str, TaskData]:
    tasks = fetch_tasks()
    id_to_task_dict: dict[str, TaskData] = {}
    for task in tasks:
        id_to_task_dict[task['id']] = task
    
    return id_to_task_dict



    
    
