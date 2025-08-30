import React, { useEffect, useRef } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Box, Typography } from '@mui/material';
import { RootState } from '../store';
import { fetchServices } from '../store/slices/servicesSlice';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const MetricsChart: React.FC = () => {
  const dispatch = useDispatch();
  const services = useSelector((state: RootState) => state.services.services);
  const chartRef = useRef<ChartJS<'line'>>(null);

  useEffect(() => {
    dispatch(fetchServices() as any);
  }, [dispatch]);

  const chartData = {
    labels: services.map(service => service.name),
    datasets: [
      {
        label: 'CPU Usage (%)',
        data: services.map(service => service.metrics.cpu),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1,
      },
      {
        label: 'Memory Usage (%)',
        data: services.map(service => service.metrics.memory),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        tension: 0.1,
      },
      {
        label: 'Response Time (ms)',
        data: services.map(service => service.metrics.responseTime),
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        tension: 0.1,
        yAxisID: 'y1',
      },
    ],
  };

  const options = {
    responsive: true,
    interaction: {
      mode: 'index' as const,
      intersect: false,
    },
    scales: {
      y: {
        type: 'linear' as const,
        display: true,
        position: 'left' as const,
        title: {
          display: true,
          text: 'Usage (%)',
        },
      },
      y1: {
        type: 'linear' as const,
        display: true,
        position: 'right' as const,
        grid: {
          drawOnChartArea: false,
        },
        title: {
          display: true,
          text: 'Response Time (ms)',
        },
      },
    },
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'System Performance Metrics',
      },
    },
  };

  if (services.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          No metrics data available
        </Typography>
      </Box>
    );
  }

  return <Line ref={chartRef} data={chartData} options={options} />;
};

export default MetricsChart;
