# SADS Deployment Guide

## 1. Local Deployment
Run the SADS stack using Docker Compose:
```bash
docker-compose up --build
```
This builds and starts the FastAPI server on port 8000 and the React application.

## 2. Production Deployment
Production stacks deploy to Kubernetes. Configuration manifests are located in `deployment/kubernetes/`.
