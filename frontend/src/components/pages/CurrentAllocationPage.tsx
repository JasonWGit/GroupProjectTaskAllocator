import { Box, Typography } from "@mui/material"
import { useEffect, useState } from "react";
import fetchFromBackend from "../../helperFunctions";

type Allocation = Record<string, string[]>;

export default function CurrentAllocationPage() {
  const [currAllocation, setCurrAllocation] = useState<Allocation>({});
  
  useEffect(() => {
    const fetchAllocation = async () => {
      const response = await fetchFromBackend("/get_allocation", "GET");
      setCurrAllocation(response);
    }

    fetchAllocation();
  }, [])

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', alignItems: 'center', justifyContent: 'center', gap: 3}}>
      <Typography>Viewing: Current Allocation</Typography>
      {Object.entries(currAllocation).map(([worker_id, task_ids]) => (
        <Box sx={{ display: 'flex', flexDirection: 'column'}}>
          <Typography>worker: {worker_id}</Typography>
          {task_ids.map(task_id => <Typography>
            task: {task_id}
          </Typography>)}
        </Box>
      )
        
      )}
      
    </Box>
  )
}