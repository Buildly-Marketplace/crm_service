# ForgeCRM 

**Complete Customer Relationship Management microservice with comprehensive business automation features.**

[![License: BSL-1.1](https://img.shields.io/badge/License-BSL--1.1-blue.svg)](LICENSE.md)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](BUILDLY.yaml)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](ops/Dockerfile)
[![Kubernetes](https://img.shields.io/badge/kubernetes-helm--chart-blue.svg)](ops/helm/forge-crm)

## What is ForgeCRM?

ForgeCRM is a Django-based CRM microservice that provides complete customer relationship management capabilities through a REST API. Built for the Buildly ecosystem, it offers account management, lead tracking, opportunity pipeline, task management, and campaign analytics.

**Key Features:**
- 📊 **Account & Contact Management** - Comprehensive customer data with flexible fields
- 🎯 **Lead Tracking & Conversion** - From lead capture to opportunity conversion
- 💰 **Sales Pipeline Management** - Opportunity tracking with forecasting and analytics  
- ✅ **Task & Activity Management** - Assignment, tracking, and completion workflows
- 📈 **Campaign Management** - Marketing campaign planning and performance analytics
- 🔐 **Secure API** - Token-based authentication with comprehensive permissions
- 🐳 **Production Ready** - Docker containers and Kubernetes Helm charts included

## Quick Start

**Docker (Recommended)**
```bash
git clone https://github.com/buildly-marketplace/crm_service.git
cd crm_service
docker-compose -f ops/docker-compose.yml up -d
curl http://localhost:8003/health/
```

**Kubernetes**
```bash
helm install forge-crm ./ops/helm/forge-crm
```

## Documentation

📚 **Complete documentation is in [`devdocs/`](devdocs/)**

- **[Setup Guide](devdocs/SETUP.md)** - Installation, configuration, and first run
- **[Operations Guide](devdocs/OPERATIONS.md)** - Production deployment and maintenance  
- **[API Reference](devdocs/REFERENCE.md)** - Complete endpoint documentation with examples
- **[Release Notes](devdocs/RELEASE_NOTES.md)** - Version history and changes

## API Overview

```bash
# Get authentication token
curl -X POST http://localhost:8003/api-token-auth/ \
  -d '{"username": "admin", "password": "admin"}'

# List accounts
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8003/accounts/

# Create lead  
curl -H "Authorization: Token YOUR_TOKEN" \
  -X POST http://localhost:8003/leads/ \
  -d '{"full_name": "John Doe", "email": "john@company.com", "status": "new"}'
```

Interactive API docs available at `/docs/` when running.

## Deployment Targets

- 🐳 **Docker** - Single container with docker-compose
- ☸️ **Kubernetes** - Helm chart with auto-scaling support  
- 💻 **Development** - Local setup with hot reload

## Support & Licensing

- **License**: BSL 1.1 → Apache 2.0 (converts November 4, 2026)
- **Support**: 30-day installation and configuration support included
- **Community**: GitHub issues for bug reports and feature requests

See [`SUPPORT.md`](SUPPORT.md) for detailed support information.

## Requirements

- Python 3.11+
- PostgreSQL 13+ (with hstore extension)
- Docker & Docker Compose (for containerized deployment)

## Health & Monitoring

```bash
# Health check
curl http://localhost:8003/health/
# Returns: {"status": "healthy", "database": "connected", "version": "1.0.0"}
```

## Contributing

This project follows the [Buildly Way](https://buildly.io/docs/buildly-way) for marketplace-ready microservices. 

1. Check existing issues and documentation
2. Follow the project structure and testing guidelines
3. Update documentation in `devdocs/` for any changes
4. Ensure smoke tests pass: `python tests/smoke_tests.py`

---

**Built with ❤️ by [Buildly Labs](https://buildly.io)** | **Available in [Buildly Forge](https://forge.buildly.io)**