from dataclasses import dataclass
from pydantic import BaseModel
from models.task import Task
from models.worker import Worker
from models.task_graph.task_graph import TaskGraph
from repositories.task_repo import fetch_tasks
from repositories.worker_repo import fetch_workers
from interfaces.serializable import Serializable
from services.task_service import get_task_id_to_task_dict
from services.worker_service import get_worker_id_to_worker_dict
import math
from collections import defaultdict
import heapq

@dataclass
class AllocationItem(Serializable):
    worker: Worker
    tasks: list[Task]

    def to_dict(self) -> dict:
        task_dict_list: list[dict] = [task.to_dict() for task in self.tasks]
        
        return {
            "worker": self.worker,
            "tasks": task_dict_list
        }

class Allocator:
    # naive allocation algorithm, just allocates tasks evenly among workers. returns a
    def do_naive_allocation(self) -> list[AllocationItem]:
        tasks = fetch_tasks()
        workers: list[Worker] = fetch_workers()

        task_graph: TaskGraph = TaskGraph(tasks)
        topological_order_tasks = task_graph.topological_sort()
        # tasks: list[Task] = do_topological_sort()
        
        if len(topological_order_tasks) == 0 or len(workers) == 0:
            return {}

        tasks_per_worker = len(tasks) / len(workers)

        num_tasks = 0
        allocationList: list[AllocationItem] = []

        for worker in workers:
            curr_worker_tasks: list[Task] = []
            num_tasks = 0
            while num_tasks < tasks_per_worker:
                if len(tasks) != 0:
                    curr_worker_tasks.append(tasks[0])
                    tasks.pop(0)
                num_tasks += 1
            
            newAllocationItem: AllocationItem = AllocationItem(worker =  worker, tasks = curr_worker_tasks)
            allocationList.append(newAllocationItem)

        return allocationList
    
    def do_greedy_allocation(self) -> list[AllocationItem]:
        tasks = fetch_tasks()
        workers = fetch_workers()

        # --------------------- preprocessing -------------------
        task_graph = TaskGraph(tasks)
        ordered_tasks: list[Task] = task_graph.topological_sort()

        # maps worker id to finish time of last assigned task for that worker
        worker_last_task_time_dict: dict[str, int] = {}
        for worker in workers:
            worker_last_task_time_dict[worker.id] = 0
        
        # maps worker ids to worker
        worker_id_to_worker_map: dict[str, Worker] = get_worker_id_to_worker_dict()

        # maps task_id to number of dependent tasks still remaining to be completed
        unfinished_dependencies: dict[str, int] = {}

        # maps task.id to current finish time for a task T 
        task_finish_times: dict[str, int] = {}

        # set holding ids of tasks that are ready to be run
        ready_tasks_set: set[str] = set()

        # maps task.id to set of task ids of tasks who depend on that task 
        task_dependents: dict[str, set[str]] = {}

        # maps task.id to task
        task_id_to_task_map: dict[str, Task] = get_task_id_to_task_dict()

        for task in ordered_tasks:
            task_dependents[task.id] = set()

        for task in ordered_tasks:
            unfinished_dependencies[task.id] = len(task.dependencies)
            # finish times for tasks by default is 0
            task_finish_times[task.id] = 0

            if len(task.dependencies) == 0:
                ready_tasks_set.add(task.id)
            
            for dep_task in task.dependencies:
                task_dependents[dep_task].add(task.id)

        
        # ------------------- Greedy assignment loop --------------------
        # greedy heuristic is to select the task with the longest duration

        # dictionary to store the key value pairs of worker id: assigned tasks
        allocation_dict: dict[str, list[Task]] = {}
        for worker in workers:
            allocation_dict[worker.id] = []
        while len(ready_tasks_set) != 0:
            # greedy heuristic is to select task with longest duration
            longest_duration_ready_task: str = None
            curr_longest_duration = -1
            for ready_task_id in ready_tasks_set:
                if task_id_to_task_map[ready_task_id].duration > curr_longest_duration:
                    longest_duration_ready_task = ready_task_id

            # determine the earliest start time for that longest duration task. the earliest start time for a task corresponds to the maximum finish time for one of its dependencies
            est = max((task_finish_times[dep] for dep in task_id_to_task_map[longest_duration_ready_task].dependencies), default=0)


            
            ### having found the longest duration ready task and its earliest start time (est), we allocate it to a worker with the ability to start working on it first i.e. the worker with the smallest worker_last_task_time_dict[workerid]

            # get the worker with the smallest last task time
            chosen_worker: str = min(worker_last_task_time_dict, key = worker_last_task_time_dict.get)

            chosen_task = task_id_to_task_map[longest_duration_ready_task]
            
            # allocate the task to the worker
            allocation_dict[chosen_worker].append(chosen_task)

            # actual task_start_time is either the earliest possible start time for the task (when all its dependencies have finished) or when the first worker can start a new task, whichever is greater
            actual_task_start_time = max(worker_last_task_time_dict[chosen_worker], est)

            actual_task_finish_time = actual_task_start_time + chosen_task.duration

            # update finish time of this task
            task_finish_times[longest_duration_ready_task] = actual_task_finish_time

            # update worker_last_task finish time to be the finish time of this new task that has been allocated to them
            worker_last_task_time_dict[chosen_worker] = actual_task_finish_time

            # decrement number of unfinished tasks in longest_duration_ready_task
            for dependent in task_dependents[longest_duration_ready_task]:
                unfinished_dependencies[dependent] -= 1
                
                # add a dependent task to ready set if it has no more unfinished dependencies
                if unfinished_dependencies[dependent] == 0:
                    ready_tasks_set.add(dependent)
            
            # remove our allocated task from the ready tasks set
            ready_tasks_set.remove(longest_duration_ready_task)
        
        allocation_items: list[AllocationItem] = []
        
        for worker_id, tasks in allocation_dict.items():
            curr_worker = worker_id_to_worker_map[worker_id]
            allocation_items.append(AllocationItem(worker=curr_worker, tasks=tasks))
        
        return allocation_items

    def do_dp_allocation(self) -> list[AllocationItem]:
        tasks = fetch_tasks()
        workers = fetch_workers()
        n = len(tasks)
        m = len(workers)

        # if no workers/tasks, nothing to schedule
        if n == 0 or m == 0:
            return []

        # preprocess task graph (topological sort so that we process/allocate all dependencies for a task before considering the task)
        # create id_to_index and index_to_task maps to allow for quick mapping between task.id <-> index in bitmask. Bitmask is used in DP where each bit represents a task and is either 0 (task not finished/allocated) or 1 (task finished/allocated)
        task_graph = TaskGraph(tasks)
        ordered_tasks = task_graph.topological_sort()
        id_to_index = {task.id: i for i, task in enumerate(ordered_tasks)}
        index_to_task = {i: task for i, task in enumerate(ordered_tasks)}

        # create a "dependencies" mask for each task i. The mask represents all the tasks that must be finished before that task i can be started. 
        # There are n dependency masks, 1 for each of the n tasks -> these masks are stored inside "prereq mask" at the index corresponding to that tasks position inside the topological ordering
        # the dependency mask for each task i has a n bits (a bit for every single task). A bit being 1 means the task it represents is a dependency task for task i
        prereq_mask = [0] * n
        durations = [t.duration for t in ordered_tasks]
        for i, task in enumerate(ordered_tasks):
            mask = 0
            for dep in task.dependencies:
                mask |= (1 << id_to_index[dep])
            prereq_mask[i] = mask

        # dp[S] stores the minimum time to finish all tasks in subset S i.e. the cached result to a subproblem
        # subsets are represented as bitmasks (S goes from 0 to 2^n - 1)
        INF = float('inf')
        dp = [INF] * (1 << n)
        dp[0] = 0
        parent = [-1] * (1 << n)
        parent_subset = [0] * (1 << n)

        # helper func to count set bits in given bitmask
        def popcount(x: int) -> int:
            return bin(x).count("1")

        # enumerate all states
        for S in range(1 << n):
            if dp[S] == INF:
                continue

            # find ready tasks (tasks that have all dependencies already allocated/finshed)
            ready_mask = 0
            for i in range(n):
                if not (S >> i) & 1:  # task not done
                    if (prereq_mask[i] & S) == prereq_mask[i]:
                        ready_mask |= (1 << i)

            if ready_mask == 0:
                continue

            # enumerate all subsets of ready tasks that can fit on workers
            sub = ready_mask
            while sub:
                if popcount(sub) <= m:
                    # compute batch duration, a batch being one possible subset of the ready tasks ->(max duration of tasks in subset)
                    batch_duration = 0
                    x = sub
                    while x:
                        lsb = x & -x
                        idx = lsb.bit_length() - 1
                        batch_duration = max(batch_duration, durations[idx])
                        x ^= lsb

                    newS = S | sub
                    new_time = dp[S] + batch_duration
                    if new_time < dp[newS]:
                        dp[newS] = new_time
                        parent[newS] = S
                        parent_subset[newS] = sub
                sub = (sub - 1) & ready_mask

        # reconstruct batches
        full_mask = (1 << n) - 1
        batches = []
        cur = full_mask
        while cur != 0:
            prev = parent[cur]
            sub = parent_subset[cur]
            task_indices = []
            x = sub
            while x:
                lsb = x & -x
                idx = lsb.bit_length() - 1
                task_indices.append(idx)
                x ^= lsb
            batches.append((task_indices, dp[prev]))
            cur = prev
        batches.reverse()

        
        # build planned start/end per task from DP task batches (subsets)
        task_planned_start: dict[int, int] = {}
        task_planned_end: dict[int, int] = {}
        for task_indices, batch_start in batches:
            for idx in task_indices:
                task_planned_start[idx] = batch_start
                task_planned_end[idx] = batch_start + durations[idx]

        # sort all tasks by planned start -> if same planned start, tie break based on duration (longer task prioritised)
        all_tasks_sorted = sorted(
            [(task_planned_start[idx], -durations[idx], idx) for idx in task_planned_start],
            key=lambda t: (t[0], t[1])
        )

        # assign tasks to workers using min-heap of (available_time, worker_index)
        worker_list = list(workers)  # index -> Worker object
        worker_heap = [(0, i) for i in range(len(worker_list))]  # (available_time, worker_index)
        heapq.heapify(worker_heap)

        worker_alloc: dict[str, list[Task]] = defaultdict(list)
        task_actual_start: dict[int, int] = {}
        task_actual_end: dict[int, int] = {}

        for planned_start, neg_dur, idx in all_tasks_sorted:
            dur = durations[idx]
            avail_time, widx = heapq.heappop(worker_heap)

            # start task at planned_start if worker free, otherwise at worker availability
            actual_start = planned_start if avail_time <= planned_start else avail_time
            actual_end = actual_start + dur

            task_obj = index_to_task[idx]
            worker_obj = worker_list[widx]

            worker_alloc[worker_obj.id].append(task_obj)

            # push worker back with new availability
            heapq.heappush(worker_heap, (actual_end, widx))

            # store actual start and end times
            task_actual_start[idx] = actual_start
            task_actual_end[idx] = actual_end
        
        

        # wrap allocation items while preserving worker order
        worker_id_to_worker = {w.id: w for w in workers}
        allocation_items: list[AllocationItem] = []
        for w in worker_list:
            allocation_items.append(AllocationItem(worker=worker_id_to_worker[w.id], tasks=worker_alloc.get(w.id, [])))

        # could potentially in future return task_actual_start/task_actual_end for gantt rendering instead of manually recalculating the start and end times in gantt service
        return allocation_items
    
    # -------------------- old batch DP (unoptimal) algorithm
    # def do_dp_allocation(self) -> list[AllocationItem]:
    #     tasks = fetch_tasks()
    #     workers = fetch_workers()
    #     m = len(workers)
    #     if len(tasks) == 0 or m == 0:
    #         return []

    #     # ----------------- Preprocessing -----------------
    #     task_graph = TaskGraph(tasks)
    #     ordered_tasks: list[Task] = task_graph.topological_sort()

    #     # map task.id -> index (0..n-1) for bitmask DP
    #     id_to_index = {task.id: i for i, task in enumerate(ordered_tasks)}
    #     index_to_id = {i: task.id for i, task in enumerate(ordered_tasks)}

    #     n = len(ordered_tasks)
    #     full_mask = (1 << n) - 1

    #     durations = [t.duration for t in ordered_tasks]
    #     prereq_mask = [0] * n
    #     for t in ordered_tasks:
    #         mask = 0
    #         for dep in t.dependencies:
    #             mask |= (1 << id_to_index[dep])
    #         prereq_mask[id_to_index[t.id]] = mask

    #     # ----------------- DP Arrays -----------------
    #     INF = 10**18
    #     dp = [INF] * (1 << n)
    #     dp[0] = 0
    #     parent = [-1] * (1 << n)
    #     parent_subset = [0] * (1 << n)

    #     # helper
    #     def popcount(x: int) -> int:
    #         return x.bit_count() if hasattr(x, "bit_count") else bin(x).count("1")

    #     # ----------------- DP Loop -----------------
    #     for S in range(1 << n):
    #         if dp[S] == INF:
    #             continue

    #         # compute ready set
    #         ready_mask = 0
    #         for i in range(n):
    #             if not (S >> i) & 1:  # task not done
    #                 if (prereq_mask[i] & S) == prereq_mask[i]:
    #                     ready_mask |= (1 << i)

    #         if ready_mask == 0:
    #             continue

    #         # enumerate submasks
    #         sub = ready_mask
    #         while sub:
    #             if popcount(sub) <= m:
    #                 # compute batch duration
    #                 max_d = 0
    #                 x = sub
    #                 while x:
    #                     lsb = x & -x
    #                     idx = lsb.bit_length() - 1
    #                     max_d = max(max_d, durations[idx])
    #                     x ^= lsb
    #                 newS = S | sub
    #                 new_time = dp[S] + max_d
    #                 if new_time < dp[newS]:
    #                     dp[newS] = new_time
    #                     parent[newS] = S
    #                     parent_subset[newS] = sub
    #             sub = (sub - 1) & ready_mask

    #     # ----------------- Reconstruct batches -----------------
    #     batches = []
    #     cur = full_mask
    #     while cur != 0:
    #         prev = parent[cur]
    #         sub = parent_subset[cur]
    #         start_time = dp[prev]
    #         task_indices = []
    #         x = sub
    #         while x:
    #             lsb = x & -x
    #             idx = lsb.bit_length() - 1
    #             task_indices.append(idx)
    #             x ^= lsb
    #         batches.append((start_time, task_indices))
    #         cur = prev
    #     batches.reverse()

    #     # ----------------- Assign tasks to workers -----------------
    #     worker_alloc: dict[str, list[Task]] = defaultdict(list)
    #     worker_id_to_worker_map: dict[str, Worker] = get_worker_id_to_worker_dict()

    #     # simple assignment: distribute tasks in each batch round-robin among workers
    #     for _, task_indices in batches:
    #         for j, idx in enumerate(task_indices):
    #             task_id = index_to_id[idx]
    #             task_obj = next(t for t in tasks if t.id == task_id)
    #             worker = workers[j % m]  # round robin
    #             worker_alloc[worker.id].append(task_obj)

    #     # ----------------- Wrap in AllocationItem -----------------
    #     allocation_items: list[AllocationItem] = []
    #     for worker_id, assigned_tasks in worker_alloc.items():
    #         worker = worker_id_to_worker_map[worker_id]
    #         allocation_items.append(AllocationItem(worker=worker, tasks=assigned_tasks))

    #     return allocation_items