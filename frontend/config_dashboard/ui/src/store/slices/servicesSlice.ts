import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_GATEWAY_URL || 'http://localhost:8080';

export interface ServiceHealth {
  id: string;
  name: string;
  status: 'healthy' | 'degraded' | 'down';
  lastCheck: string;
  metrics: {
    cpu: number;
    memory: number;
    responseTime: number;
  };
}

interface ServicesState {
  services: ServiceHealth[];
  loading: boolean;
  error: string | null;
}

const initialState: ServicesState = {
  services: [],
  loading: false,
  error: null,
};

export const fetchServices = createAsyncThunk(
  'services/fetchServices',
  async () => {
    const response = await axios.get(`${API_URL}/services`);
    return response.data;
  }
);

export const servicesSlice = createSlice({
  name: 'services',
  initialState,
  reducers: {
    updateServiceHealth: (state, action) => {
      const { id, status } = action.payload;
      const service = state.services.find(s => s.id === id);
      if (service) {
        service.status = status;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchServices.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchServices.fulfilled, (state, action) => {
        state.loading = false;
        state.services = action.payload;
      })
      .addCase(fetchServices.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch services';
      });
  },
});

export const { updateServiceHealth } = servicesSlice.actions;
export default servicesSlice.reducer;
