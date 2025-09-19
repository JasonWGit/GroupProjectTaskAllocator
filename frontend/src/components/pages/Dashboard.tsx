import { Box, TextField, Typography, Button, Link } from '@mui/material';
import { useState, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../../supabase';
import fetchFromBackend from '../../helperFunctions';

export default function Dashboard() {
  const [rootData, setRootData] = useState(null);
  const navigate = useNavigate();

  const navCreateTasks = () => {
    navigate("/create_tasks");
  }

  const navAllocation = () => {
    navigate("/allocation_page")
  }

  const navCurrAllocation = () => {
    navigate("/curr_allocation")
  }

  const navViewGraph = () => {
    navigate("/view_graph");
  }

  return (
    <>
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: "center", height: "100%", flexDirection: "column" }}>
        <Typography variant="h3" sx={{ mb: 5 }}>Dashboard</Typography>
        <Button variant="contained" sx={{ mb: 5 }} onClick={navCreateTasks}>Go to create tasks page</Button>
        <Button variant="contained" onClick={navAllocation} sx={{ mb: 5 }}>Go to allocation page</Button>
        <Button variant="contained" onClick={navCurrAllocation} sx={{ mb: 5 }}>Go to current allocation page</Button>
        <Button variant="contained" onClick={navViewGraph}>view task graph</Button>
      </Box>
    </>
  )
}

