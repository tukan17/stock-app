'use client';

import { Box, Paper } from '@mui/material';
import { DataGrid, type GridColDef } from '@mui/x-data-grid';

// Mock data - replace with real data from your API
const columns: GridColDef[] = [
  { field: 'symbol', headerName: 'Symbol', width: 130 },
  { field: 'name', headerName: 'Name', width: 200 },
  { field: 'shares', headerName: 'Shares', width: 130, type: 'number' },
  {
    field: 'averagePrice',
    headerName: 'Avg. Price',
    width: 130,
    type: 'number',
    valueFormatter: (params) => {
      return `$${params.value.toFixed(2)}`;
    },
  },
  {
    field: 'currentPrice',
    headerName: 'Current Price',
    width: 130,
    type: 'number',
    valueFormatter: (params) => {
      return `$${params.value.toFixed(2)}`;
    },
  },
  {
    field: 'marketValue',
    headerName: 'Market Value',
    width: 130,
    type: 'number',
    valueFormatter: (params) => {
      return `$${params.value.toLocaleString()}`;
    },
  },
  {
    field: 'gain',
    headerName: 'Gain/Loss',
    width: 130,
    type: 'number',
    cellClassName: (params) => {
      return params.value >= 0 ? 'positive' : 'negative';
    },
    valueFormatter: (params) => {
      return `${params.value >= 0 ? '+' : ''}$${params.value.toLocaleString()}`;
    },
  },
  {
    field: 'gainPercent',
    headerName: 'Gain/Loss %',
    width: 130,
    type: 'number',
    cellClassName: (params) => {
      return params.value >= 0 ? 'positive' : 'negative';
    },
    valueFormatter: (params) => {
      return `${params.value >= 0 ? '+' : ''}${params.value.toFixed(2)}%`;
    },
  },
];

const rows = [
  {
    id: 1,
    symbol: 'AAPL',
    name: 'Apple Inc.',
    shares: 100,
    averagePrice: 150.00,
    currentPrice: 170.50,
    marketValue: 17050,
    gain: 2050,
    gainPercent: 13.67,
  },
  // Add more mock data as needed
];

export default function PortfolioPage() {
  return (
    <Box sx={{ height: 'calc(100vh - 150px)', width: '100%' }}>
      <Paper sx={{ height: '100%', width: '100%' }}>
        <DataGrid
          rows={rows}
          columns={columns}
          pageSizeOptions={[10, 25, 50]}
          initialState={{
            pagination: {
              paginationModel: {
                pageSize: 10,
              },
            },
          }}
          sx={{
            '& .positive': {
              color: 'success.main',
            },
            '& .negative': {
              color: 'error.main',
            },
          }}
        />
      </Paper>
    </Box>
  );
}