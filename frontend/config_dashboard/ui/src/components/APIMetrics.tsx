import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Box,
  Typography,
  Grid,
  Paper,
} from '@mui/material';
import { RootState } from '../store';
import { fetchAPIMetrics } from '../store/slices/apiSlice';

const APIMetrics: React.FC = () => {
  const dispatch = useDispatch();
  const metrics = useSelector((state: RootState) => state.api.metrics);
  const loading = useSelector((state: RootState) => state.api.loading);

  useEffect(() => {
    dispatch(fetchAPIMetrics() as any);
  }, [dispatch]);

  if (loading) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="body2">Loading API metrics...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Grid container spacing={2}>
        <Grid item xs={6}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="primary" gutterBottom>
              {metrics.totalRequests.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Requests
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={6}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="success.main" gutterBottom>
              {metrics.successRate.toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Success Rate
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={6}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="info.main" gutterBottom>
              {metrics.averageResponseTime.toFixed(0)}ms
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Avg Response Time
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={6}>
          <Paper sx={{ p: 2, textAlign: 'center' }}>
            <Typography variant="h6" color="error.main" gutterBottom>
              {metrics.errorRate.toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Error Rate
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default APIMetrics;
