# Contributing to VF Logistics

## Team SORA

| Member | Role | Responsibilities |
|--------|------|-----------------|
| Chau Phuoc Hoa | Team Lead / Backend | Snowflake procedures, AI pipeline, Agent, CI/CD |
| Nguyen Quoc Cuong | Frontend Developer | Mendix UI, workflow, user experience |

## Development Workflow

### Branch Strategy
```
main        — Production-ready code (protected)
develop     — Integration branch
feature/*   — New features
fix/*       — Bug fixes
```

### Setup Local Development

1. Install Snowflake CoCo CLI (Cortex Code Desktop)
2. Connect to Snowflake account
3. Run setup script:
```sql
-- Deploy all objects
SOURCE 'SETUP_PIPELINE_COMPLETE.sql';
```

### Making Changes

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes to SQL/Python files
3. Test locally via CoCo CLI
4. Push and create PR → CI runs automatically
5. After review, merge to main → CD deploys to Snowflake

### SQL Style Guide

- Use UPPERCASE for SQL keywords: `SELECT`, `FROM`, `WHERE`
- Use snake_case for object names: `bill_of_lading`, `port_master`
- Prefix views with `V_`: `V_AI_DAILY_COST`
- Prefix procedures with descriptive names: `CLASSIFY_`, `CHECK_`, `DETECT_`
- Always include error handling with TRY/CATCH in procedures
- Log AI calls to `AI_CALL_LOG` for monitoring

### Testing

Run the test suite:
```bash
# CI runs automatically on PR
# Manual trigger: Actions → Test → Run workflow
```

### Security Rules

- NEVER commit `.p8` or `.pem` key files
- NEVER hardcode passwords or tokens
- Use GitHub Secrets for CI/CD credentials
- Follow least-privilege principle for roles
