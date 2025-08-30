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
  Code as CodeIcon,
  PlayArrow as PlayArrowIcon,
  CheckCircle as CheckCircleIcon,
  Block as BlockIcon,
} from '@mui/icons-material';
import { RootState } from '../store';
import { fetchModels } from '../store/slices/modelsSlice';

const MLModelsList: React.FC = () => {
  const dispatch = useDispatch();
  const models = useSelector((state: RootState) => state.models.models);
  const loading = useSelector((state: RootState) => state.models.loading);

  useEffect(() => {
    dispatch(fetchModels() as any);
  }, [dispatch]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'deployed':
        return <CheckCircleIcon color="success" />;
      case 'training':
        return <PlayArrowIcon color="warning" />;
      case 'development':
        return <CodeIcon color="info" />;
      case 'deprecated':
        return <BlockIcon color="error" />;
      default:
        return <CodeIcon />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'deployed':
        return 'success';
      case 'training':
        return 'warning';
      case 'development':
        return 'info';
      case 'deprecated':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatLastUpdated = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="body2">Loading models...</Typography>
      </Box>
    );
  }

  if (models.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          No ML models available
        </Typography>
      </Box>
    );
  }

  return (
    <List dense>
      {models.map((model) => (
        <ListItem key={model.id} divider>
          <ListItemIcon>
            {getStatusIcon(model.status)}
          </ListItemIcon>
          <ListItemText
            primary={
              <Box display="flex" alignItems="center" gap={1}>
                <Typography variant="body2" component="span">
                  {model.name} v{model.version}
                </Typography>
                <Chip
                  label={model.status}
                  color={getStatusColor(model.status) as any}
                  size="small"
                />
              </Box>
            }
            secondary={
              <Box>
                <Typography variant="caption" color="text.secondary" display="block">
                  Type: {model.type.toUpperCase()}
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Accuracy: {model.metrics.accuracy.toFixed(2)}%
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Updated: {formatLastUpdated(model.lastUpdated)}
                </Typography>
              </Box>
            }
          />
        </ListItem>
      ))}
    </List>
  );
};

export default MLModelsList;
