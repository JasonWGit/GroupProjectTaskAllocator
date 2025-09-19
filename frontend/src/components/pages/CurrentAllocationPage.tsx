import { Box, Typography } from "@mui/material"
import { useEffect, useState } from "react";
import fetchFromBackend from "../../helperFunctions";

type WorkerData = {
  name: string;
  id: string;
}

type TaskData = {
  name: string;
  description: string;
  duration: number;
  dependencies: string[]
  id: string;
}

type AllocationItem = {
  worker: WorkerData;
  tasks: TaskData[];
}

type Allocation = AllocationItem[];
// type FormattedAllocation = Record<WorkerData, TaskData[]>;

export default function CurrentAllocationPage() {
  // allocation mapping worker id to task ids they are allocated to
  const [currAllocation, setCurrAllocation] = useState<Allocation>([]);

  // a formatted allocation mapping worker names to task names
  // const [formattedAllocation, setFormattedAllocation] = useState<FormattedAllocation>([]);
  
  useEffect(() => {
    const fetchAllocation = async () => {
      const response = await fetchFromBackend("/get_allocation", "GET");
      // const response2 = await fetchFromBackend("/get_allocation_formatted", "GET");
      setCurrAllocation(response);
      // setFormattedAllocation(response2);
    }

    fetchAllocation();
  }, [])

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', alignItems: 'center', justifyContent: 'center', gap: 3}}>
      <Typography>Viewing: Current Allocation</Typography>
      {/* {Object.entries(formattedAllocation).map(([worker_name, task_names]) => (
        <Box sx={{ display: 'flex', flexDirection: 'column'}} key={Math.random()}>
          <Typography>worker: {worker_name}</Typography>
          {task_names.map(task_name => <Typography key={Math.random()}>
            task: {task_name}
          </Typography>)}
        </Box>
      )
      )} */}

      {currAllocation.map(({ worker, tasks }) => (
        <Box sx={{ display: 'flex', flexDirection: 'column' }} key={worker.id}>
          <Typography>worker: {worker.name}</Typography>
          {tasks.map(task => 
            <Typography key={task.id}>
              task: {task.name}
            </Typography>
          )}
        </Box>
      ))}
    </Box>
  )
}