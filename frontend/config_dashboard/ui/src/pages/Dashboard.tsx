import React from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import { useSelector } from 'react-redux';
import { RootState } from '../store';  
import ServiceHealthCard from '../components/ServiceHealthCard';
import MetricsChart from '../components/MetricsChart';
import AlertsList from '../components/AlertsList';
import MLModelsList from '../components/MLModelsList';
import APIMetrics from '../components/APIMetrics';

const Dashboard: React.FC = () => {
  const services = useSelector((state: RootState) => state.services.services);
  
  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Grid container spacing={3}>
        {/* Service Health Overview */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Service Health
            </Typography>
            <Grid container spacing={2}>
              {services.map((service) => (
                <Grid item xs={12} sm={6} md={4} key={service.id}>
                  <ServiceHealthCard service={service} />
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>

        {/* Performance Metrics */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              System Performance
            </Typography>
            <MetricsChart />
          </Paper>
        </Grid>

        {/* Active Alerts */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Active Alerts
            </Typography>
            <AlertsList />
          </Paper>
        </Grid>

        {/* ML Models Status */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              ML Models Status
            </Typography>
            <MLModelsList />
          </Paper>
        </Grid>

        {/* API Metrics */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              API Usage
            </Typography>
            <APIMetrics />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
