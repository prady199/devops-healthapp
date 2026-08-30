# DevSecOps Security Controls — Healthcare Patient Portal

Security is enforced by the pipeline itself, not by a manual review at the end.
A build that violates a control never reaches the cluster.

## Pipeline security gates

| Stage | Tool | What it catches | Blocks build |
|-------|------|-----------------|--------------|
| SAST | Bandit | Insecure code patterns in Python source | Yes, on HIGH severity |
| Secret scan | Trivy | API keys, tokens, passwords committed to Git | Yes, on any finding |
| Dependency scan | Trivy | Known CVEs in third-party libraries | Reports HIGH and CRITICAL |
| Image scan | Trivy | CVEs in OS packages inside the container image | Yes, on CRITICAL |

Scanning happens **before** the image is pushed, so a vulnerable artefact never
reaches the registry.

## Runtime controls in Kubernetes

| Control | Implementation | Risk addressed |
|---------|----------------|----------------|
| Non-root execution | `runAsNonRoot`, uid 10001 | Container escape gains an unprivileged account |
| Read-only filesystem | `readOnlyRootFilesystem: true` | Attacker cannot write malware or tamper with code |
| Capability dropping | `capabilities.drop: ["ALL"]` | Removes raw socket, mount, and admin syscalls |
| No privilege escalation | `allowPrivilegeEscalation: false` | Blocks setuid escalation to root |
| Seccomp | `RuntimeDefault` profile | Restricts the available syscall surface |
| Resource limits | CPU and memory caps | Contains denial of service from one pod |
| Secret management | Kubernetes Secret populated from the Jenkins credential store | Credentials never exist in Git or in build logs |
| RBAC | `healthapp-sa` with zero permissions, token not mounted | A compromised pod cannot query the cluster API |
| Scoped CI identity | `ci-deployer` role limited to this namespace, no Secret access | Limits blast radius of stolen CI credentials |
| Network ingress policy | Only TCP 5000 accepted | Reduces lateral movement surface |
| Network egress policy | DNS only | Prevents exfiltration of patient data |
| Audit logging | Every access to `/api/patients` recorded with source IP and decision | Supports the accountability requirements of health data regulation |
| Authentication | `X-API-Key` header validated on every patient data request | Prevents anonymous access to records |

## Mapping to healthcare requirements

Health data regulation generally requires access control, audit trails,
transmission security, and integrity controls. This build addresses them as
follows:

- **Access control** — API key authentication plus Kubernetes RBAC
- **Audit trail** — structured allow/deny logging on every record access
- **Integrity** — read-only filesystem and immutable, digest-tagged images
- **Least privilege** — non-root containers, empty service account, scoped roles
- **Containment** — network policies and namespace isolation

## Deliberate design decisions

- Patient records in this build are entirely synthetic. No real protected
  health information is used anywhere in the repository.
- The application refuses to start if no API key is supplied, so a
  misconfigured deployment fails closed rather than serving data openly.
- The pipeline prints scan reports to the console and archives them as build
  artefacts, giving each release an evidence trail.

## Known limitations

This is a coursework build on a single-node cluster. A production system would
additionally require TLS termination with real certificates, an external secret
manager such as AWS Secrets Manager or HashiCorp Vault rather than plain
Kubernetes Secrets (which are only base64 encoded at rest by default),
encryption of etcd, image signing and admission control, and centralised log
aggregation with alerting.
