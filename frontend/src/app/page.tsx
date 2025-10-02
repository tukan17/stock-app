'use client';

import {
  Container,
  Typography,
  Box,
  Grid,
  Paper,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Timeline,
  TrendingUp,
  AccountBalance,
  Security,
} from '@mui/icons-material';
import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

const features = [
  {
    icon: <TrendingUp color="primary" />,
    title: 'Real-time Portfolio Tracking',
    description: 'Monitor your investments in real-time with automatic updates and price tracking.',
  },
  {
    icon: <Timeline color="primary" />,
    title: 'Performance Analytics',
    description: 'Detailed performance metrics, charts, and insights to help you make informed decisions.',
  },
  {
    icon: <AccountBalance color="primary" />,
    title: 'Multi-broker Support',
    description: 'Connect with multiple brokers and manage all your investments in one place.',
  },
  {
    icon: <Security color="primary" />,
    title: 'Secure & Private',
    description: 'Bank-grade security to keep your financial data safe and protected.',
  },
];

export default function Home() {
  const { data: session } = useSession();
  const router = useRouter();

  if (session) {
    router.push('/dashboard');
    return null;
  }

  return (
    <Container maxWidth="lg">
      {/* Hero Section */}
      <Box
        sx={{
          pt: 8,
          pb: 6,
          textAlign: 'center',
        }}
      >
        <Typography
          component="h1"
          variant="h2"
          color="primary"
          gutterBottom
          sx={{
            fontWeight: 700,
            fontSize: { xs: '2.5rem', md: '3.5rem' },
          }}
        >
          Stock Portfolio Tracker
        </Typography>
        <Typography
          variant="h5"
          color="text.secondary"
          paragraph
          sx={{ mb: 4 }}
        >
          Your all-in-one solution for tracking and managing your investment portfolio.
          Get real-time updates, insightful analytics, and comprehensive reporting tools.
        </Typography>
        <Box sx={{ mt: 4 }}>
          <Button
            component={Link}
            href="/auth/login"
            variant="contained"
            size="large"
            sx={{ mx: 1 }}
          >
            Get Started
          </Button>
          <Button
            component={Link}
            href="/auth/login"
            variant="outlined"
            size="large"
            sx={{ mx: 1 }}
          >
            Sign In
          </Button>
        </Box>
      </Box>

      {/* Features Section */}
      <Box sx={{ py: 8 }}>
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Paper
                sx={{
                  p: 4,
                  height: '100%',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4,
                  },
                }}
                elevation={2}
              >
                <Box sx={{ display: 'flex', alignItems: 'flex-start' }}>
                  <Box sx={{ mr: 2 }}>{feature.icon}</Box>
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      {feature.title}
                    </Typography>
                    <Typography variant="body1" color="text.secondary">
                      {feature.description}
                    </Typography>
                  </Box>
                </Box>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Benefits Section */}
      <Box sx={{ py: 8 }}>
        <Typography variant="h4" gutterBottom textAlign="center" sx={{ mb: 4 }}>
          Why Choose Our Platform?
        </Typography>
        <Grid container spacing={4}>
          <Grid item xs={12} md={6}>
            <List>
              <ListItem>
                <ListItemIcon>
                  <TrendingUp color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary="Comprehensive Portfolio Management"
                  secondary="Track stocks, ETFs, mutual funds, and cryptocurrencies in one place"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Timeline color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary="Advanced Analytics"
                  secondary="Get detailed insights into your portfolio performance and risk metrics"
                />
              </ListItem>
            </List>
          </Grid>
          <Grid item xs={12} md={6}>
            <List>
              <ListItem>
                <ListItemIcon>
                  <AccountBalance color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary="Automated Dividend Tracking"
                  secondary="Never miss a dividend payment with automated tracking and notifications"
                />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <Security color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary="Industry-Standard Security"
                  secondary="Your data is protected with enterprise-grade encryption and security measures"
                />
              </ListItem>
            </List>
          </Grid>
        </Grid>
      </Box>

      {/* Call to Action */}
      <Box
        sx={{
          py: 8,
          textAlign: 'center',
          backgroundColor: 'primary.main',
          color: 'primary.contrastText',
          borderRadius: 2,
          mt: 4,
          mb: 8,
        }}
      >
        <Typography variant="h4" gutterBottom>
          Ready to Take Control of Your Portfolio?
        </Typography>
        <Typography variant="subtitle1" sx={{ mb: 4 }}>
          Join thousands of investors who trust our platform for their portfolio management needs.
        </Typography>
        <Button
          component={Link}
          href="/auth/login"
          variant="contained"
          size="large"
          sx={{
            backgroundColor: 'common.white',
            color: 'primary.main',
            '&:hover': {
              backgroundColor: 'grey.100',
            },
          }}
        >
          Start For Free
        </Button>
      </Box>
    </Container>
  );
}