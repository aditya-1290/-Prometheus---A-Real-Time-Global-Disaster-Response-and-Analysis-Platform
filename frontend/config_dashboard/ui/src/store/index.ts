import { configureStore } from '@reduxjs/toolkit';
import { servicesSlice } from './slices/servicesSlice';
import { modelsSlice } from './slices/modelsSlice';
import { alertsSlice } from './slices/alertsSlice';
import { apiSlice } from './slices/apiSlice';

export const store = configureStore({
  reducer: {
    services: servicesSlice.reducer,
    models: modelsSlice.reducer,
    alerts: alertsSlice.reducer,
    api: apiSlice.reducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
