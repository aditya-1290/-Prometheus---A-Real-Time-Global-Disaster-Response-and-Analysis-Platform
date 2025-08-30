import React from 'react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { ServiceHealth } from '../store/slices/servicesSlice';

interface ServiceHealthCardProps {
  service: ServiceHealth;
}

const ServiceHealthCard: React.FC<ServiceHealthCardProps> = ({ service }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'down':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatLastCheck = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <Card sx={{ minWidth: 275 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="div">
            {service.name}
          </Typography>
          <Chip 
            label={service.status} 
            color={getStatusColor(service.status) as any}
            size="small"
          />
        </Box>
        
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Last check: {formatLastCheck(service.lastCheck)}
        </Typography>
        
        <Box mt={2}>
          <Typography variant="caption" color="text.secondary" display="block">
            CPU: {service.metrics.cpu}%
          </Typography>
          <Typography variant="caption" color="text.secondary" display="block">
            Memory: {service.metrics.memory}%
          </Typography>
          <Typography variant="caption" color="text.secondary" display="block">
            Response: {service.metrics.responseTime}ms
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ServiceHealthCard;
