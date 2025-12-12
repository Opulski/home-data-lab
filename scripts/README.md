# Scripts

This directory contains utility scripts for development, deployment, and maintenance.

## Categories

- **Setup**: Environment setup and initialization scripts
- **Deploy**: Deployment and release scripts
- **Utils**: Helper scripts for common tasks
- **Maintenance**: Database migrations, cleanup, etc.

## Guidelines

- Make scripts executable (`chmod +x`)
- Include usage documentation in script headers
- Use shell script best practices
- Add error handling and validation
- Make scripts idempotent when possible

## Examples

```bash
# Setup local development environment
./scripts/setup-dev.sh

# Deploy to staging
./scripts/deploy.sh staging

# Run database migrations
./scripts/migrate-db.sh
```
