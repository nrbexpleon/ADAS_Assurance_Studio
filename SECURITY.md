# Security policy

Report vulnerabilities privately through GitHub Security Advisories. Do not commit customer sensor data, faces, number plates, VINs, map extracts, credentials, signing keys or private thresholds.

The server binds to loopback, bounds request bodies, supports an optional bearer token and has no vehicle-control interface. Production deployment requires OIDC/RBAC, TLS, tenant isolation, rate limiting, durable audit storage, data-retention controls and independent cybersecurity review.
