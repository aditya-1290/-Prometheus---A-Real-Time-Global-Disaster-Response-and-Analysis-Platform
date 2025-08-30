import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Box,
  Typography,
} from '@mui/material';
import {
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { RootState } from '../store';
import { fetchAlerts } from '../store/slices/alertsSlice';

const AlertsList: React.FC = () => {
  const dispatch = useDispatch();
  const alerts = useSelector((state: RootState) => state.alerts.alerts);
  const loading = useSelector((state: RootState) => state.alerts.loading);

  useEffect(() => {
    dispatch(fetchAlerts() as any);
  }, [dispatch]);

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="body2">Loading alerts...</Typography>
      </Box>
    );
  }

  if (alerts.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          No active alerts
        </Typography>
      </Box>
    );
  }

  return (
    <List dense>
      {alerts.map((alert) => (
        <ListItem key={alert.id} divider>
          <ListItemIcon>
            {getSeverityIcon(alert.severity)}
          </ListItemIcon>
          <ListItemText
            primary={
              <Box display="flex" alignItems="center" gap={1}>
                <Typography variant="body2" component="span">
                  {alert.message}
                </Typography>
                <Chip
                  label={alert.severity}
                  color={getSeverityColor(alert.severity) as any}
                  size="small"
                />
              </Box>
            }
            secondary={
              <Typography variant="caption" color="text.secondary">
                {formatTimestamp(alert.timestamp)}
                {alert.resolved && ' • Resolved'}
              </Typography>
            }
          />
        </ListItem>
      ))}
    </List>
  );
};

export default AlertsList;
