import React, { useEffect, useState } from 'react';
import { getJobs } from '../services/api';

const Dashboard = () => {
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await getJobs();
        setJobs(res.data);
      } catch (err) {
        console.error("Failed to fetch jobs:", err);
      }
    };
    fetchJobs();
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      <p>You have applied to {jobs.length} jobs.</p>
    </div>
  );
};

export default Dashboard;
