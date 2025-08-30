import React from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Paper,
  Grid,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';

interface DamageData {
  location: string;
  severity: number;
  affectedArea: number;
  infrastructure: {
    type: string;
    damageLevel: number;
  }[];
}

interface DamageAssessmentProps {
  damageData: DamageData[];
}

const DamageAssessment: React.FC<DamageAssessmentProps> = ({ damageData }) => {
  const chartData = {
    labels: damageData.map(d => d.location),
    datasets: [
      {
        label: 'Damage Severity',
        data: damageData.map(d => d.severity),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1
      }
    ]
  };

  const infrastructureData = {
    labels: ['Buildings', 'Roads', 'Power', 'Water', 'Communications'],
    datasets: [
      {
        label: 'Infrastructure Damage Level',
        data: damageData.reduce((acc, curr) => {
          curr.infrastructure.forEach(inf => {
            const index = acc.findIndex(a => a.type === inf.type);
            if (index !== -1) {
              acc[index].total += inf.damageLevel;
            }
          });
          return acc;
        }, []),
        backgroundColor: 'rgba(54, 162, 235, 0.5)'
      }
    ]
  };

  return (
    <div>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Typography variant="h6">Damage Assessment Overview</Typography>
          <Paper style={{ padding: '20px' }}>
            <Line data={chartData} />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Typography variant="h6">Infrastructure Impact</Typography>
          <Paper style={{ padding: '20px' }}>
            <Bar data={infrastructureData} />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Typography variant="h6">Detailed Assessment</Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Location</TableCell>
                  <TableCell>Severity</TableCell>
                  <TableCell>Affected Area (km²)</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {damageData.map((data, index) => (
                  <TableRow key={index}>
                    <TableCell>{data.location}</TableCell>
                    <TableCell>{data.severity}</TableCell>
                    <TableCell>{data.affectedArea}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Grid>
      </Grid>
    </div>
  );
};

export default DamageAssessment;
