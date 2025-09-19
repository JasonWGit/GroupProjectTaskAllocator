import { useState } from 'react'
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom';
import Dashboard from './components/pages/Dashboard';
import { AppBar, Button, Toolbar, Link } from '@mui/material';
import './App.css'
import InputTaskPage from './components/pages/InputTaskPage';
import AllocationPage from './components/pages/AllocationPage';
import CurrentAllocationPage from './components/pages/CurrentAllocationPage';
import ViewGraphPage from './components/pages/ViewGraphPage';

function NavBar() {
  const navigate = useNavigate();

  const navHome = () => {
    navigate("/")
  }

  return (
    <>
      <AppBar position="relative">
        <Toolbar>
          <Button variant="contained" onClick={navHome}>HOME</Button>
        </Toolbar>
      </AppBar>
    </>
  )
}

function App() {
  return (
    <>
      
      
      <BrowserRouter>
        <NavBar>
        </NavBar>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/create_tasks" element={<InputTaskPage />} />
          <Route path="/allocation_page" element={<AllocationPage />} />
          <Route path="/curr_allocation" element={<CurrentAllocationPage />} />
          <Route path="/view_graph" element={<ViewGraphPage />} />
        </Routes>
      </BrowserRouter>
    </>
  )
}

export default App
