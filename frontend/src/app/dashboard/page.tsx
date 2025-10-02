'use client';

import { Grid, Paper, Typography, Box } from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

// Mock data - replace with real data from your API
const portfolioData = {
  totalValue: 125000,
  dailyChange: 1250,
  dailyChangePercent: 1.01,
  allocation: [
    { name: 'Stocks', value: 70000, color: '#1976d2' },
    { name: 'Bonds', value: 30000, color: '#2e7d32' },
    { name: 'Cash', value: 25000, color: '#ed6c02' },
  ],
};

export default function DashboardPage() {
  return (
    <Grid container spacing={3}>
      {/* Portfolio Value */}
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 3, height: '100%' }}>
          <Typography variant="h6" gutterBottom>
            Total Portfolio Value
          </Typography>
          <Typography variant="h3" component="div">
            ${portfolioData.totalValue.toLocaleString()}
          </Typography>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              mt: 1,
              color: portfolioData.dailyChange >= 0 ? 'success.main' : 'error.main',
            }}
          >
            <Typography variant="body1">
              {portfolioData.dailyChange >= 0 ? '+' : ''}$
              {portfolioData.dailyChange.toLocaleString()} (
              {portfolioData.dailyChangePercent.toFixed(2)}%)
            </Typography>
          </Box>
        </Paper>
      </Grid>

      {/* Asset Allocation */}
      <Grid item xs={12} md={8}>
        <Paper sx={{ p: 3, height: '100%' }}>
          <Typography variant="h6" gutterBottom>
            Asset Allocation
          </Typography>
          <Box sx={{ height: 300 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={portfolioData.allocation}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ name, percent }) =>
                    `${name} ${(percent * 100).toFixed(0)}%`
                  }
                >
                  {portfolioData.allocation.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </Box>
        </Paper>
      </Grid>

      {/* Recent Transactions */}
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Recent Transactions
          </Typography>
          {/* Add TransactionList component here */}
        </Paper>
      </Grid>
    </Grid>
  );
}