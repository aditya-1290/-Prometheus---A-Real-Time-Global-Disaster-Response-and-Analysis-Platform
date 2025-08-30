import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Chip,
} from '@mui/material';
import PublicMap from './PublicMap';
import { Resource } from '@/types/api';
import { resourceService } from '@/services/api';

const ResourceLocator: React.FC = () => {
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResources = async () => {
      try {
        const response = await resourceService.getAvailableResources();
        setResources(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to load resource data');
        console.error('Error fetching resources:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchResources();
  }, []);

  const getStatusColor = (status: Resource['status']) => {
    switch (status) {
      case 'available':
        return 'success';
      case 'allocated':
        return 'warning';
      case 'depleted':
        return 'error';
      default:
        return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={2}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
        <Typography variant="h5" gutterBottom>
          Available Resources
        </Typography>
        
        <Box mb={4}>
          <PublicMap
            center={[0, 0]}
            zoom={2}
            markers={resources.map(resource => ({
              position: [resource.location.latitude, resource.location.longitude],
              title: resource.name,
              type: resource.type,
              status: resource.status
            }))}
          />
        </Box>

        <Grid container spacing={2}>
          {resources.map((resource) => (
            <Grid item xs={12} sm={6} md={4} key={resource.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {resource.name}
                  </Typography>
                  <Typography color="textSecondary" gutterBottom>
                    {resource.type}
                  </Typography>
                  <Box mt={1}>
                    <Chip
                      label={resource.status}
                      color={getStatusColor(resource.status)}
                      size="small"
                    />
                  </Box>
                  <Typography variant="body2" mt={1}>
                    Quantity: {resource.quantity}
                  </Typography>
                  {resource.location.address && (
                    <Typography variant="body2" mt={1}>
                      Location: {resource.location.address}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Box>
  );
};

export default ResourceLocator;
