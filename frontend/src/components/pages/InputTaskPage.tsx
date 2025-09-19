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
  [key: string]: any;
}

interface DependencyInputProps {
  selectedTaskDependencies: SelectedTask[];
  setSelectedTaskDependencies: React.Dispatch<React.SetStateAction<SelectedTask[]>>;
  choosableTasks: ChoosableTask[];
  setChoosableTasks: React.Dispatch<React.SetStateAction<ChoosableTask[]>>;
  fetchTasks: () => Promise<void>;
}



function DependencyInputFormField({ selectedTaskDependencies, setSelectedTaskDependencies, choosableTasks, setChoosableTasks, fetchTasks }: DependencyInputProps) {
  useEffect(() => {
    fetchTasks();
  }, [])
  
  /* add a choosable task to the list of selected task dependencies */
  const handleClickTaskBtn = (e: React.MouseEvent<HTMLButtonElement>, task: ChoosableTask) => {
    e.preventDefault();
    console.log(selectedTaskDependencies);
    const newSelectedTask: SelectedTask = task;

    // after choosing a task by clicking it, remove it from the list of available tasks
    setChoosableTasks((prev) => choosableTasks.filter(task => task.id != newSelectedTask.id));

    // add the selected task to the list of selected tasks
    setSelectedTaskDependencies((prev) => [...prev, newSelectedTask]);
  }

  const handleClickSelectedTaskBtn = (e: React.MouseEvent<HTMLButtonElement>, task: SelectedTask) => {
    e.preventDefault();
    console.log('hi');
    const newChoosableTask: ChoosableTask = task;
    setSelectedTaskDependencies((prev) => selectedTaskDependencies.filter(selected_task => selected_task.id != task.id));
    
    setChoosableTasks((prev) => [...prev, newChoosableTask]);
  }

  return (
    <>
      <Box sx={{ display: 'flex', gap: 1, maxWidth: "90%", flexWrap: "wrap" }}>
        <Typography sx={{width: '100%'}}>Available task dependencies</Typography>
        {
          choosableTasks.map(task => 
            <button type="button" key = {task.id}onClick={(e: React.MouseEvent<HTMLButtonElement>) => handleClickTaskBtn(e, task)}>{task.name}</button>
          )
        }
      </Box>

      <Box sx={{ display: 'flex', gap: 1, maxWidth: "90%", flexWrap: "wrap" }}>
        <Typography sx={{ width: '100% '}}>Selected task dependencies</Typography><br></br>

        {
          selectedTaskDependencies.map(task => 
            <button type="button" key = {task.id} onClick={(e: React.MouseEvent<HTMLButtonElement>) =>
              handleClickSelectedTaskBtn(e, task)
            }>{task.name}</button>
          )
        }
      </Box>
    </>
  )
}

export default function InputTaskPage() {
  const fetchTasks = async (): Promise<void> => {
    const response = await fetchFromBackend("/get_tasks", "GET");
    console.log(response);
    setChoosableTasks(response)
  }

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
  const [choosableTasks, setChoosableTasks] = useState<ChoosableTask[]>([]);

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

  const taskFormSubmitHandler = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();

    await fetchFromBackend("/create_task", "POST", {
      name: taskFormData.name.value,
      description: taskFormData.description.value,
      duration: taskFormData.duration.value,
      dependencies: selectedTaskDependencies.map(task => task.id)
    });
    // reset the task form upon submit
    setTaskFormData(initialTaskFormData);
    setSelectedTaskDependencies([])
    fetchTasks();
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
            setSelectedTaskDependencies={setSelectedTaskDependencies}
            choosableTasks={choosableTasks}
            setChoosableTasks={setChoosableTasks}
            fetchTasks={fetchTasks}
          />
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