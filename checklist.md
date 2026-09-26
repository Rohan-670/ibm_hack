# Release & Onboarding Checklist

## Release-relevant
- [ ] Security review completed for any new external-facing endpoint
- [ ] Rollback plan documented for schema or contract changes
- [ ] No secrets or credentials hardcoded in source
- [ ] Database/data migrations are reversible
- [ ] Breaking API changes are called out in CHANGELOG.md with a version bump

## Onboarding-relevant
- [ ] All environment variables the app reads are listed in `.env.example`
- [ ] Setup steps are documented in README.md and actually work from a clean checkout
- [ ] The test command is documented and passes on a clean checkout
