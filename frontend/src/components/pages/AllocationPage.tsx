import { Box, Button, Typography } from "@mui/material";
import { useState, useEffect } from "react";
import fetchFromBackend from "../../helperFunctions";

interface Task {
  id: string;
  name: string;
  description: string;
  duration: number;
  dependencies: string[];
}

interface Worker {
  id: string;
  name: string;
}

export default function AllocationPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [workers, setWorkers] = useState<Worker[]>([]);

  useEffect(() => {
    const fetchTasks = async () => {
      const response = await fetchFromBackend("/get_tasks", "GET");
      setTasks(response);
    }

    const fetchWorkers = async () => {
      const response = await fetchFromBackend("/get_workers", "GET");
      setWorkers(response);
    }

    fetchTasks();
    fetchWorkers();
  }, []);

  const handleClickDoAllocation = async () => {
    const response = await fetchFromBackend("/get_allocation", "GET");
    console.log(response);
  }
  return (
    <>
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <Typography>Current tasks</Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1}}>
        {
          tasks.map(task => 
            <Box sx={{ backgroundColor: 'lightblue', p: 1}}key={task.id}>  
              <Typography>name: {task.name}</Typography>
              <Typography>desc: {task.description}</Typography>
              <Typography>duration: {task.duration}</Typography>
              <Typography>dependencies: {task.dependencies}</Typography>
            </Box>
          )
        }
        
        </Box>
        <Typography sx={{ mt: 3}}>Current Workers</Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1}}>
          {
            workers.map(worker =>
              <Box sx={{ backgroundColor: 'lightblue', p: 1}} key={worker.id}>
                <Typography>name: {worker.name}</Typography>
              </Box>
            )
          }



        </Box>
        <Button variant="contained" sx={{mt: 3}} onClick={handleClickDoAllocation}>do allocation</Button>
      </Box>
    </>
  )
}