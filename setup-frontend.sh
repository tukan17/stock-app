#!/bin/bash

# Create frontend directory if it doesn't exist
mkdir -p frontend/src/{app,auth,components,types}

# Create necessary directories
mkdir -p frontend/src/app/{auth/login,dashboard,portfolio,transactions,settings}
mkdir -p frontend/src/app/api/auth/[...nextauth]

# Copy configuration files
echo '{
  "name": "stock-app-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "@mui/icons-material": "^5.11.16",
    "@mui/material": "^5.13.0",
    "@mui/x-data-grid": "^6.4.0",
    "@tanstack/react-query": "^4.29.5",
    "axios": "^1.4.0",
    "date-fns": "^2.30.0",
    "next": "13.4.12",
    "next-auth": "^4.22.1",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "react-hook-form": "^7.43.9",
    "recharts": "^2.6.2",
    "typescript": "5.0.4",
    "zod": "^3.21.4",
    "zustand": "^4.3.8"
  },
  "devDependencies": {
    "@types/node": "18.16.3",
    "@types/react": "18.2.0",
    "@types/react-dom": "18.2.1",
    "eslint": "8.39.0",
    "eslint-config-next": "13.3.4",
    "prettier": "^2.8.8"
  }
}' > frontend/package.json

echo '{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}' > frontend/tsconfig.json

echo 'NEXTAUTH_SECRET=your-secret-key
NEXT_PUBLIC_API_URL=http://localhost:8000' > frontend/.env.local

# Install dependencies
cd frontend && npm install

# Initialize git repository if not already initialized
git init

# Add .gitignore
echo 'node_modules/
.next/
.env.local
.env.*.local
tsconfig.tsbuildinfo' > .gitignore

# Stage all files
git add .

# Commit the changes
git commit -m "Initial frontend setup"