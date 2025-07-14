# DevOps Project Management API

A complete DevOps implementation with Flask, Docker, Terraform, and CI/CD.

## Features
- REST API for project management
- Containerized with Docker
- Infrastructure as Code with Terraform
- Automated CI/CD with GitHub Actions
- Deployed on AWS EC2

## Tech Stack
- Python Flask
- PostgreSQL
- Docker & Docker Compose
- Terraform
- GitHub Actions
- AWS (VPC, EC2, Security Groups)

## Quick Start
```bash
git clone https://github.com/AYHALOUI/project-management-devops.git
cd project-management-devops
docker-compose up --build
```

## API Endpoints
- GET /projects - List projects
- POST /projects - Create project
- GET /projects/:id/tasks - Get tasks
- POST /projects/:id/tasks - Create task

## Infrastructure
Deployed using Terraform on AWS with automated CI/CD pipeline.

