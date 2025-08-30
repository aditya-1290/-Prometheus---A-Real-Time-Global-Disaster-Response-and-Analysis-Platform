import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import { Resource, EmergencyRequest } from '../types/api';
import { resourceService } from '../services/api';

interface ResourceAllocationProps {
  resources: Resource[];
  emergencies: EmergencyRequest[];
  onAllocationUpdate: () => void;
}

const ResourceAllocation: React.FC<ResourceAllocationProps> = ({
  resources,
  emergencies,
  onAllocationUpdate
}) => {
  const [open, setOpen] = useState(false);
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);
  const [selectedEmergency, setSelectedEmergency] = useState<string>('');
  const [quantity, setQuantity] = useState<number>(1);

  const handleAllocate = async () => {
    if (!selectedResource || !selectedEmergency) return;

    try {
      await resourceService.allocateResource(
        selectedResource.id,
        selectedEmergency,
        quantity
      );
      onAllocationUpdate();
      setOpen(false);
    } catch (error) {
      console.error('Failed to allocate resource:', error);
    }
  };

  return (
    <div>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Resource</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Available Quantity</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {resources.map((resource) => (
              <TableRow key={resource.id}>
                <TableCell>{resource.name}</TableCell>
                <TableCell>{resource.type}</TableCell>
                <TableCell>{resource.quantity}</TableCell>
                <TableCell>{resource.status}</TableCell>
                <TableCell>
                  <Button
                    variant="contained"
                    color="primary"
                    disabled={resource.status !== 'available'}
                    onClick={() => {
                      setSelectedResource(resource);
                      setOpen(true);
                    }}
                  >
                    Allocate
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Allocate Resource</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel>Emergency</InputLabel>
            <Select
              value={selectedEmergency}
              onChange={(e) => setSelectedEmergency(e.target.value)}
            >
              {emergencies.map((emergency) => (
                <MenuItem key={emergency.id} value={emergency.id}>
                  {emergency.type} - {emergency.priority}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            type="number"
            label="Quantity"
            value={quantity}
            onChange={(e) => setQuantity(Number(e.target.value))}
            margin="normal"
            InputProps={{ inputProps: { min: 1, max: selectedResource?.quantity } }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleAllocate} color="primary">
            Allocate
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  );
};

export default ResourceAllocation;
