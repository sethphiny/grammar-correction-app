#!/bin/bash

# Set environment variables to bypass ESLint conflicts
export DISABLE_ESLINT_PLUGIN=true
export SKIP_PREFLIGHT_CHECK=true

# Start the React development server
echo "Starting React development server with ESLint conflicts disabled..."
pnpm start
