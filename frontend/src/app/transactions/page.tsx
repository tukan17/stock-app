'use client';

import { useState } from 'react';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper,
  TextField,
  MenuItem,
} from '@mui/material';
import { DataGrid, type GridColDef } from '@mui/x-data-grid';
import { useForm } from 'react-hook-form';

// Mock data - replace with real data from your API
const columns: GridColDef[] = [
  { field: 'date', headerName: 'Date', width: 130 },
  { field: 'type', headerName: 'Type', width: 130 },
  { field: 'symbol', headerName: 'Symbol', width: 130 },
  { field: 'shares', headerName: 'Shares', width: 130, type: 'number' },
  {
    field: 'price',
    headerName: 'Price',
    width: 130,
    type: 'number',
    valueFormatter: (params) => {
      return `$${params.value.toFixed(2)}`;
    },
  },
  {
    field: 'total',
    headerName: 'Total',
    width: 130,
    type: 'number',
    valueFormatter: (params) => {
      return `$${params.value.toFixed(2)}`;
    },
  },
];

const rows = [
  {
    id: 1,
    date: '2023-10-01',
    type: 'BUY',
    symbol: 'AAPL',
    shares: 10,
    price: 170.50,
    total: 1705.00,
  },
  // Add more mock data as needed
];

interface TransactionFormData {
  type: 'BUY' | 'SELL';
  symbol: string;
  shares: number;
  price: number;
  date: string;
}

export default function TransactionsPage() {
  const [open, setOpen] = useState(false);
  const { register, handleSubmit, reset } = useForm<TransactionFormData>();

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
    reset();
  };

  const onSubmit = (data: TransactionFormData) => {
    // Handle form submission
    console.log(data);
    handleClose();
  };

  return (
    <Box sx={{ height: 'calc(100vh - 150px)', width: '100%' }}>
      <Box sx={{ mb: 2 }}>
        <Button variant="contained" onClick={handleClickOpen}>
          Add Transaction
        </Button>
      </Box>

      <Paper sx={{ height: 'calc(100% - 48px)', width: '100%' }}>
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
        />
      </Paper>

      <Dialog open={open} onClose={handleClose}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogTitle>Add New Transaction</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'grid', gap: 2, mt: 2 }}>
              <TextField
                select
                label="Type"
                {...register('type')}
                defaultValue="BUY"
              >
                <MenuItem value="BUY">Buy</MenuItem>
                <MenuItem value="SELL">Sell</MenuItem>
              </TextField>

              <TextField
                label="Symbol"
                {...register('symbol')}
                placeholder="e.g., AAPL"
              />

              <TextField
                type="number"
                label="Shares"
                {...register('shares')}
                inputProps={{ step: 'any' }}
              />

              <TextField
                type="number"
                label="Price per Share"
                {...register('price')}
                inputProps={{ step: '0.01' }}
              />

              <TextField
                type="date"
                label="Date"
                {...register('date')}
                InputLabelProps={{ shrink: true }}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleClose}>Cancel</Button>
            <Button type="submit" variant="contained">
              Add Transaction
            </Button>
          </DialogActions>
        </form>
      </Dialog>
    </Box>
  );
}