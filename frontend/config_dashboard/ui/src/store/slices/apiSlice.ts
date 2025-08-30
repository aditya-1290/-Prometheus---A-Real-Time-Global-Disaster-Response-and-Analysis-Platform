import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_GATEWAY_URL || 'http://localhost:8080';

export interface APIKey {
  id: string;
  name: string;
  key: string;
  type: 'internal' | 'external' | 'partner';
  active: boolean;
  lastUsed?: string;
}

export interface APIMetrics {
  totalRequests: number;
  successRate: number;
  averageResponseTime: number;
  errorRate: number;
}

interface APIState {
  keys: APIKey[];
  metrics: APIMetrics;
  loading: boolean;
  error: string | null;
}

const initialState: APIState = {
  keys: [],
  metrics: {
    totalRequests: 0,
    successRate: 0,
    averageResponseTime: 0,
    errorRate: 0,
  },
  loading: false,
  error: null,
};

export const fetchAPIKeys = createAsyncThunk(
  'api/fetchKeys',
  async () => {
    const response = await axios.get(`${API_URL}/api-keys`);
    return response.data;
  }
);

export const createAPIKey = createAsyncThunk(
  'api/createKey',
  async (keyData: Omit<APIKey, 'id' | 'key' | 'lastUsed'>) => {
    const response = await axios.post(`${API_URL}/api-keys`, keyData);
    return response.data;
  }
);

export const revokeAPIKey = createAsyncThunk(
  'api/revokeKey',
  async (keyId: string) => {
    await axios.delete(`${API_URL}/api-keys/${keyId}`);
    return keyId;
  }
);

export const fetchAPIMetrics = createAsyncThunk(
  'api/fetchMetrics',
  async () => {
    const response = await axios.get(`${API_URL}/api-metrics`);
    return response.data;
  }
);

export const apiSlice = createSlice({
  name: 'api',
  initialState,
  reducers: {
    updateMetrics: (state, action) => {
      state.metrics = { ...state.metrics, ...action.payload };
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAPIKeys.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchAPIKeys.fulfilled, (state, action) => {
        state.loading = false;
        state.keys = action.payload;
      })
      .addCase(fetchAPIKeys.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch API keys';
      })
      .addCase(createAPIKey.fulfilled, (state, action) => {
        state.keys.push(action.payload);
      })
      .addCase(revokeAPIKey.fulfilled, (state, action) => {
        state.keys = state.keys.filter(key => key.id !== action.payload);
      })
      .addCase(fetchAPIMetrics.fulfilled, (state, action) => {
        state.metrics = action.payload;
      });
  },
});
