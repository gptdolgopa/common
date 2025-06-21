# gRPC UI Sandbox

This repository contains a simple UI for executing gRPC requests similar to Postman.

## Structure

- `grpcui/backend` – FastAPI server that executes requests using `grpcurl`.
- `grpcui/frontend` – React based interface (Vite).

## Running

1. Start the backend:
   ```bash
   uvicorn grpcui.backend.app:app --reload
   ```
2. Start the frontend:
   ```bash
   cd grpcui/frontend
   npm install
   npm run dev
   ```

The frontend proxies API requests to the backend using the `/api` prefix.
