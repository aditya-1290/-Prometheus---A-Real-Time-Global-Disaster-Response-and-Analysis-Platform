import React, { useState } from 'react';
import {
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Typography,
  Paper
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Edit as EditIcon,
  Notifications as NotificationsIcon
} from '@mui/icons-material';

interface Alert {
  id: string;
  type: string;
  message: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  recipients: string[];
  status: 'pending' | 'sent' | 'failed';
}

interface AlertManagementProps {
  alerts: Alert[];
  onAlertCreate: (alert: Omit<Alert, 'id' | 'status'>) => void;
  onAlertDelete: (id: string) => void;
  onAlertUpdate: (id: string, alert: Partial<Alert>) => void;
}

const AlertManagement: React.FC<AlertManagementProps> = ({
  alerts,
  onAlertCreate,
  onAlertDelete,
  onAlertUpdate
}) => {
  const [open, setOpen] = useState(false);
  const [editingAlert, setEditingAlert] = useState<Alert | null>(null);
  const [formData, setFormData] = useState({
    type: '',
    message: '',
    severity: 'info' as Alert['severity'],
    recipients: [] as string[]
  });

  const handleSubmit = () => {
    if (editingAlert) {
      onAlertUpdate(editingAlert.id, formData);
    } else {
      onAlertCreate(formData);
    }
    setOpen(false);
    setEditingAlert(null);
    setFormData({
      type: '',
      message: '',
      severity: 'info',
      recipients: []
    });
  };

  const handleEdit = (alert: Alert) => {
    setEditingAlert(alert);
    setFormData({
      type: alert.type,
      message: alert.message,
      severity: alert.severity,
      recipients: alert.recipients
    });
    setOpen(true);
  };

  return (
    <div>
      <Paper style={{ padding: '20px', marginBottom: '20px' }}>
        <Typography variant="h6" gutterBottom>
          Alert Management
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<NotificationsIcon />}
          onClick={() => setOpen(true)}
          style={{ marginBottom: '20px' }}
        >
          Create New Alert
        </Button>

        <List>
          {alerts.map((alert) => (
            <ListItem
              key={alert.id}
              style={{
                borderLeft: `4px solid ${
                  alert.severity === 'critical'
                    ? '#ff1744'
                    : alert.severity === 'error'
                    ? '#f44336'
                    : alert.severity === 'warning'
                    ? '#ffeb3b'
                    : '#2196f3'
                }`
              }}
            >
              <ListItemText
                primary={alert.type}
                secondary={
                  <>
                    <Typography component="span" variant="body2">
                      {alert.message}
                    </Typography>
                    <br />
                    <Typography component="span" variant="caption">
                      Status: {alert.status}
                    </Typography>
                  </>
                }
              />
              <ListItemSecondaryAction>
                <IconButton
                  edge="end"
                  aria-label="edit"
                  onClick={() => handleEdit(alert)}
                >
                  <EditIcon />
                </IconButton>
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={() => onAlertDelete(alert.id)}
                >
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>
          {editingAlert ? 'Edit Alert' : 'Create New Alert'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Type"
            value={formData.type}
            onChange={(e) =>
              setFormData({ ...formData, type: e.target.value })
            }
            margin="normal"
          />
          <TextField
            fullWidth
            label="Message"
            value={formData.message}
            onChange={(e) =>
              setFormData({ ...formData, message: e.target.value })
            }
            margin="normal"
            multiline
            rows={4}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Severity</InputLabel>
            <Select
              value={formData.severity}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  severity: e.target.value as Alert['severity']
                })
              }
            >
              <MenuItem value="info">Info</MenuItem>
              <MenuItem value="warning">Warning</MenuItem>
              <MenuItem value="error">Error</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Recipients (comma-separated)"
            value={formData.recipients.join(', ')}
            onChange={(e) =>
              setFormData({
                ...formData,
                recipients: e.target.value.split(',').map((r) => r.trim())
              })
            }
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} color="primary">
            {editingAlert ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default AlertManagement;
