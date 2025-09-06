import { Box, Button, TextField, Typography } from "@mui/material";
import { useState, useEffect } from 'react';
import fetchFromBackend from "../../helperFunctions";

interface ChoosableTask {
  name: string;
  id: string;
  [key: string]: any;
}

interface SelectedTask {
  id: string;
  name: string;
}

interface DependencyInputProps {
  selectedTaskDependencies: SelectedTask[];
  setSelectedTaskDependencies: React.Dispatch<React.SetStateAction<SelectedTask[]>>;
}

function DependencyInputFormField({ selectedTaskDependencies, setSelectedTaskDependencies }: DependencyInputProps) {
  const [choosableTasks, setChoosableTasks] = useState<ChoosableTask[]>([]);

  useEffect(() => {
    const fetchTasks = async () => {
      const response = await fetchFromBackend("/get_tasks", "GET")
      console.log(response);
      setChoosableTasks(response)
    }

    fetchTasks();
  }, [])

  const handleClickTaskBtn = (e: React.MouseEvent<HTMLButtonElement>, taskId: string, taskName: string) => {
    e.preventDefault();
    console.log(selectedTaskDependencies);
    const newSelectedTask: SelectedTask = {
      id: taskId,
      name: taskName
    };

    // after choosing a task by clicking it, remove it from the list of available tasks
    setChoosableTasks((prev) => choosableTasks.filter(task => task.id != taskId));

    // add the selected task to the list of selected tasks
    setSelectedTaskDependencies((prev) => [...prev, newSelectedTask]);
  }

  const handleClickSelectedTaskBtn = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    console.log('hi');
  }

  return (
    <>
      <Box sx={{ display: 'flex', gap: 1, maxWidth: "90%", flexWrap: "wrap" }}>
        <Typography>Available task dependencies</Typography>
        {
          choosableTasks.map(task => 
            <button type="button" key = {task.id}onClick={(e: React.MouseEvent<HTMLButtonElement>) => handleClickTaskBtn(e, task.id, task.name)}>{task.name}</button>
          )
        }
      </Box>

      <Box sx={{ display: 'flex', gap: 1, maxWidth: "90%", flexWrap: "wrap" }}>
        <Typography>Selected task dependencies</Typography>

        {
          selectedTaskDependencies.map(task => 
            <button type="button" key = {task.id} onClick={(e: React.MouseEvent<HTMLButtonElement>) =>
              handleClickSelectedTaskBtn(e)
            }>{task.name}</button>
          )
        }
      </Box>
    </>
  )
}

export default function InputTaskPage() {
  const initialTaskFormData = {
    name: {value: ''},
    description: {value: ''},
    duration: {value: ''}
  }

  const initialWorkerFormData = {
    name: {value: ''}
  };

  const [taskFormData, setTaskFormData] = useState(initialTaskFormData);
  const [workerFormData, setWorkerFormData] = useState(initialWorkerFormData);

  const [selectedTaskDependencies, setSelectedTaskDependencies] = useState<SelectedTask[]>([]);

  const formChangeHandler = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTaskFormData((prev) => ({
      ...prev,
      [e.target.name]: { value: e.target.value }
    }));
  }

  const workerFormChangeHandler = (e: React.ChangeEvent<HTMLInputElement>) => {
    setWorkerFormData((prev) => ({
      ...prev,
      [e.target.name]: { value: e.target.value },
    }));
  }

  const taskFormSubmitHandler = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();

    fetchFromBackend("/create_task", "POST", {
      name: taskFormData.name.value,
      description: taskFormData.description.value,
      duration: taskFormData.duration.value,
      dependencies: selectedTaskDependencies.map(task => task.id)
    });
    // reset the task form upon submit
    setTaskFormData(initialTaskFormData);
    setSelectedTaskDependencies([])
  }

  const workerFormSubmitHandler = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();

    fetchFromBackend("/create_worker", "POST", {
      name: workerFormData.name.value,
    });

    setWorkerFormData(initialWorkerFormData);
  }

  return (
    <>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: "100%", flexDirection: 'column'}}>
        <Typography sx={{mb: 3}}>Input Tasks</Typography>
        <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 5}}>
          <TextField label="Task name" name="name" onChange={formChangeHandler} value={taskFormData.name.value}/>
          <TextField label="Task description" name="description" onChange={formChangeHandler} value={taskFormData.description.value}/>
          <TextField label="Task duration (minutes)" name="duration" onChange={formChangeHandler} value={taskFormData.duration.value}/>
          <DependencyInputFormField 
            selectedTaskDependencies={selectedTaskDependencies} 
            setSelectedTaskDependencies={setSelectedTaskDependencies}/>
          <Button type="submit" variant="contained" onClick={taskFormSubmitHandler}>Submit</Button>
        </Box>
        

        
        <Typography sx={{ mb: 3 }}>Input Workers</Typography>
        <Box component = "form" sx={{ display: 'flex', flexDirection: 'column', gap: 2}}>
          <TextField label="Worker name" name="name" onChange={workerFormChangeHandler} value={workerFormData.name.value}/>
          <Button type="submit" variant="contained" onClick={workerFormSubmitHandler}>Submit</Button>
          
        </Box>
      </Box>
    </>
  )
}