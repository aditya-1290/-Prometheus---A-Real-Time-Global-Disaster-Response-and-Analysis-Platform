import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const Settings: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="body1">
          Settings page is under construction. This will contain application configuration, 
          user preferences, and system settings.
        </Typography>
      </Paper>
    </Box>
  );
};

export default Settings;
