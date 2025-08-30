import React, { useEffect, useState } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Box
} from '@mui/material';
import CrisisMap from '../components/CrisisMap';
import ResourceAllocation from '../components/ResourceAllocation';
import DamageAssessment from '../components/DamageAssessment';
import AlertManagement from '../components/AlertManagement';
import { disasterService, resourceService, analyticsService } from '../services/api';
import { Disaster, Resource, Alert } from '../types/api';
import { socket } from '../services/socket';

const Dashboard: React.FC = () => {
  const [disasters, setDisasters] = useState<Disaster[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [
          disastersRes,
          resourcesRes,
          statsRes
        ] = await Promise.all([
          disasterService.getAllDisasters(),
          resourceService.getAllResources(),
          analyticsService.getDisasterStatistics()
        ]);

        setDisasters(disastersRes.data);
        setResources(resourcesRes.data);
        setStats(statsRes.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      }
    };

    fetchData();

    // Set up WebSocket listeners
    socket.on('disaster:update', (disaster: Disaster) => {
      setDisasters(prev => 
        prev.map(d => d.id === disaster.id ? disaster : d)
      );
    });

    socket.on('resource:update', (resource: Resource) => {
      setResources(prev =>
        prev.map(r => r.id === resource.id ? resource : r)
      );
    });

    socket.on('alert:new', (alert: Alert) => {
      setAlerts(prev => [...prev, alert]);
    });

    return () => {
      socket.off('disaster:update');
      socket.off('resource:update');
      socket.off('alert:new');
    };
  }, []);

  return (
    <Box p={3}>
      <Grid container spacing={3}>
        {/* Stats Overview */}
        <Grid item xs={12}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Active Disasters
                  </Typography>
                  <Typography variant="h4">
                    {stats?.active || 0}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Available Resources
                  </Typography>
                  <Typography variant="h4">
                    {resources.filter(r => r.status === 'available').length}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Active Alerts
                  </Typography>
                  <Typography variant="h4">
                    {alerts.filter(a => a.status === 'pending').length}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <CardContent>
                  <Typography color="textSecondary" gutterBottom>
                    Response Rate
                  </Typography>
                  <Typography variant="h4">
                    {stats?.responseRate || '0%'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Grid>

        {/* Crisis Map */}
        <Grid item xs={12}>
          <Paper>
            <Box p={2}>
              <Typography variant="h6" gutterBottom>
                Crisis Map
              </Typography>
              <CrisisMap disasters={disasters} />
            </Box>
          </Paper>
        </Grid>

        {/* Resource Allocation */}
        <Grid item xs={12} md={6}>
          <Paper>
            <Box p={2}>
              <Typography variant="h6" gutterBottom>
                Resource Allocation
              </Typography>
              <ResourceAllocation
                resources={resources}
                emergencies={[]} // TODO: Add emergencies state
                onAllocationUpdate={() => {
                  resourceService.getAllResources()
                    .then(res => setResources(res.data));
                }}
              />
            </Box>
          </Paper>
        </Grid>

        {/* Alert Management */}
        <Grid item xs={12} md={6}>
          <AlertManagement
            alerts={alerts}
            onAlertCreate={() => {}} // TODO: Implement alert creation
            onAlertDelete={() => {}} // TODO: Implement alert deletion
            onAlertUpdate={() => {}} // TODO: Implement alert update
          />
        </Grid>

        {/* Damage Assessment */}
        <Grid item xs={12}>
          <Paper>
            <Box p={2}>
              <Typography variant="h6" gutterBottom>
                Damage Assessment
              </Typography>
              <DamageAssessment damageData={[]} /> {/* TODO: Add damage data */}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
