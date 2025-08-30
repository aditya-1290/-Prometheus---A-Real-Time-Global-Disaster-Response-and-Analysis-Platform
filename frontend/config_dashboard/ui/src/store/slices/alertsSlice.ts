import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_GATEWAY_URL || 'http://localhost:8080';

export interface Alert {
  id: string;
  serviceId: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  message: string;
  timestamp: string;
  resolved: boolean;
  resolutionNote?: string;
}

interface AlertsState {
  alerts: Alert[];
  loading: boolean;
  error: string | null;
}

const initialState: AlertsState = {
  alerts: [],
  loading: false,
  error: null,
};

export const fetchAlerts = createAsyncThunk(
  'alerts/fetchAlerts',
  async () => {
    const response = await axios.get(`${API_URL}/alerts`);
    return response.data;
  }
);

export const resolveAlert = createAsyncThunk(
  'alerts/resolveAlert',
  async ({ alertId, resolutionNote }: { alertId: string; resolutionNote: string }) => {
    const response = await axios.post(`${API_URL}/alerts/${alertId}/resolve`, {
      resolutionNote,
    });
    return response.data;
  }
);

export const alertsSlice = createSlice({
  name: 'alerts',
  initialState,
  reducers: {
    addAlert: (state, action) => {
      state.alerts.unshift(action.payload);
    },
    updateAlert: (state, action) => {
      const { id, ...updates } = action.payload;
      const alert = state.alerts.find(a => a.id === id);
      if (alert) {
        Object.assign(alert, updates);
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAlerts.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchAlerts.fulfilled, (state, action) => {
        state.loading = false;
        state.alerts = action.payload;
      })
      .addCase(fetchAlerts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch alerts';
      })
      .addCase(resolveAlert.fulfilled, (state, action) => {
        const { id, resolved, resolutionNote } = action.payload;
        const alert = state.alerts.find(a => a.id === id);
        if (alert) {
          alert.resolved = resolved;
          alert.resolutionNote = resolutionNote;
        }
      });
  },
});
