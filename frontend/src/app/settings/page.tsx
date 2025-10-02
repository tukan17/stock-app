'use client';

import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Switch,
  Divider,
  TextField,
  Button,
} from '@mui/material';
import { useState } from 'react';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    darkMode: false,
    emailNotifications: true,
    currencyDisplay: 'USD',
  });

  const handleToggle = (setting: keyof typeof settings) => {
    setSettings((prev) => ({
      ...prev,
      [setting]: !prev[setting],
    }));
  };

  const handleCurrencyChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSettings((prev) => ({
      ...prev,
      currencyDisplay: event.target.value,
    }));
  };

  return (
    <Box sx={{ maxWidth: 600 }}>
      <Typography variant="h5" gutterBottom>
        Settings
      </Typography>

      <Paper sx={{ mt: 3 }}>
        <List>
          <ListItem>
            <ListItemText
              primary="Dark Mode"
              secondary="Enable dark color scheme"
            />
            <Switch
              edge="end"
              checked={settings.darkMode}
              onChange={() => handleToggle('darkMode')}
            />
          </ListItem>

          <Divider />

          <ListItem>
            <ListItemText
              primary="Email Notifications"
              secondary="Receive updates about your portfolio"
            />
            <Switch
              edge="end"
              checked={settings.emailNotifications}
              onChange={() => handleToggle('emailNotifications')}
            />
          </ListItem>

          <Divider />

          <ListItem>
            <ListItemText
              primary="Display Currency"
              secondary="Set your preferred currency display"
            />
            <TextField
              select
              value={settings.currencyDisplay}
              onChange={handleCurrencyChange}
              variant="outlined"
              size="small"
              sx={{ width: 100 }}
              SelectProps={{
                native: true,
              }}
            >
              <option value="USD">USD</option>
              <option value="EUR">EUR</option>
              <option value="GBP">GBP</option>
              <option value="JPY">JPY</option>
              <option value="CZK">CZK</option>
            </TextField>
          </ListItem>
        </List>
      </Paper>

      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Broker API Settings
        </Typography>
        <Paper sx={{ p: 3 }}>
          <TextField
            fullWidth
            label="API Key"
            type="password"
            margin="normal"
          />
          <TextField
            fullWidth
            label="API Secret"
            type="password"
            margin="normal"
          />
          <Button variant="contained" sx={{ mt: 2 }}>
            Save API Settings
          </Button>
        </Paper>
      </Box>
    </Box>
  );
}