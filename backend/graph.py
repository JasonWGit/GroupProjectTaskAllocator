from functions import fetch_tasks, fetch_workers, TaskData, WorkerData
from typing import Dict, Set

# file to store the graph data structure to model the task and dependencies as a DAG 
Graph = Dict[str, Set[str]]




# function that takes a list of tasks and their dependencies and constructs a graph 
def construct_graph_from_tasks(tasks: list[TaskData]):
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
    


    print(adjacencyList)
    return adjacencyList

# wrapper function to fetch tasks and input it to the above function
def construct_graph() -> Graph:
    tasks = fetch_tasks()
    return construct_graph_from_tasks(tasks)

# function that takes a graph and performs topological sort 
def topological_sort(task_graph: Graph):
    in_degrees = {u: 0 for u in task_graph}
    for u in task_graph:
       for v in task_graph[u]:
           in_degrees[v] = in_degrees.get(v, 0) + 1
    
    S = {u for u in in_degrees if in_degrees[u] == 0}
   
    topological_order = []

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
def do_topological_sort():
    task_graph = construct_graph()
    topological_order = topological_sort(task_graph)
    return topological_order
    
    
