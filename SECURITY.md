# Security Policy

## Supported Scope

This repository provides the shared security policy for the `vLLM-HUST` GitHub organization.

It applies by default to repositories that do not define a more specific local `SECURITY.md`.

## Reporting A Vulnerability

Please do not report security issues in public GitHub issues.

Instead:

1. Use GitHub Security Advisories for the affected repository when available.
2. If the repository does not expose that path yet, contact the maintainers privately and include reproduction details, impact, and affected versions.
3. Redact secrets, access tokens, internal hostnames, and customer data from all reports.

## What To Include

Please include as much of the following as you can:

- affected repository and branch or release
- concise impact statement
- reproduction steps or proof of concept
- configuration assumptions and environment details
- whether the issue is public anywhere else
- any suggested mitigation or workaround

## Coordinated Disclosure

We prefer coordinated disclosure.

After confirming a report, maintainers may:

- reproduce and triage severity
- prepare a fix privately when appropriate
- coordinate release timing across affected repositories
- publish an advisory once users have a reasonable upgrade path

## Out Of Scope

The following are usually not treated as reportable vulnerabilities by themselves:

- requests for general hardening guidance without a concrete flaw
- reports that depend on pasting live secrets into public threads
- issues in third-party services or upstream projects unless `vLLM-HUST` introduces a distinct exploit path

## Secret Handling Reminder

Never paste real PATs, API keys, private endpoints, or credentials into issues, pull requests, or CI logs.
If you accidentally expose a secret, revoke or rotate it immediately before reporting the incident.