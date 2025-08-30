import React from 'react';
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
  Paper,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import InfoIcon from '@mui/icons-material/Info';
import WarningIcon from '@mui/icons-material/Warning';
import SecurityIcon from '@mui/icons-material/Security';

interface SafetyTip {
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
}

interface DisasterGuide {
  type: string;
  description: string;
  beforeTips: SafetyTip[];
  duringTips: SafetyTip[];
  afterTips: SafetyTip[];
}

interface SafetyGuideProps {
  guides: DisasterGuide[];
}

const SafetyGuide: React.FC<SafetyGuideProps> = ({ guides }) => {
  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <WarningIcon color="error" />;
      case 'medium':
        return <SecurityIcon color="warning" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  const renderTipsList = (tips: SafetyTip[]) => (
    <List>
      {tips.map((tip, index) => (
        <ListItem key={index}>
          <ListItemIcon>
            {getPriorityIcon(tip.priority)}
          </ListItemIcon>
          <ListItemText
            primary={tip.title}
            secondary={tip.description}
            primaryTypographyProps={{
              fontWeight: tip.priority === 'high' ? 'bold' : 'normal'
            }}
          />
        </ListItem>
      ))}
    </List>
  );

  return (
    <Box>
      {guides.map((guide, index) => (
        <Paper 
          key={index}
          elevation={3}
          sx={{ mb: 2 }}
        >
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6">{guide.type}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Typography paragraph>
                {guide.description}
              </Typography>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography color="primary">Before the Disaster</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {renderTipsList(guide.beforeTips)}
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography color="error">During the Disaster</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {renderTipsList(guide.duringTips)}
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography color="success">After the Disaster</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {renderTipsList(guide.afterTips)}
                </AccordionDetails>
              </Accordion>
            </AccordionDetails>
          </Accordion>
        </Paper>
      ))}
    </Box>
  );
};

export default SafetyGuide;
