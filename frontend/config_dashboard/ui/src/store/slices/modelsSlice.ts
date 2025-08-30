import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_GATEWAY_URL || 'http://localhost:8080';

export interface MLModel {
  id: string;
  name: string;
  version: string;
  type: 'nlp' | 'cv' | 'audio' | 'multimodal';
  status: 'development' | 'training' | 'deployed' | 'deprecated';
  metrics: {
    accuracy: number;
    precision: number;
    recall: number;
    f1Score: number;
    latency: number;
  };
  lastUpdated: string;
}

interface ModelsState {
  models: MLModel[];
  loading: boolean;
  error: string | null;
}

const initialState: ModelsState = {
  models: [],
  loading: false,
  error: null,
};

export const fetchModels = createAsyncThunk(
  'models/fetchModels',
  async () => {
    const response = await axios.get(`${API_URL}/ml-models`);
    return response.data;
  }
);

export const deployModel = createAsyncThunk(
  'models/deployModel',
  async (modelId: string) => {
    const response = await axios.post(`${API_URL}/ml-models/${modelId}/deploy`);
    return response.data;
  }
);

export const modelsSlice = createSlice({
  name: 'models',
  initialState,
  reducers: {
    updateModelStatus: (state, action) => {
      const { id, status } = action.payload;
      const model = state.models.find(m => m.id === id);
      if (model) {
        model.status = status;
      }
    },
    updateModelMetrics: (state, action) => {
      const { id, metrics } = action.payload;
      const model = state.models.find(m => m.id === id);
      if (model) {
        model.metrics = { ...model.metrics, ...metrics };
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchModels.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchModels.fulfilled, (state, action) => {
        state.loading = false;
        state.models = action.payload;
      })
      .addCase(fetchModels.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch models';
      })
      .addCase(deployModel.fulfilled, (state, action) => {
        const { id, status } = action.payload;
        const model = state.models.find(m => m.id === id);
        if (model) {
          model.status = status;
        }
      });
  },
});
