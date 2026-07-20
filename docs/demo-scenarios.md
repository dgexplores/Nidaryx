# Demo Scenarios

The MVP target is six repeatable labelled scenarios. The repository currently includes the deterministic database-pool saturation path used by unit tests and the web UI.

| Scenario | Injected origin | Expected symptoms | Success signal |
| --- | --- | --- | --- |
| DB pool saturation | `mongodb` | `order-service` latency and gateway errors | `mongodb` appears Top-1 RCA |
| API latency spike | `demo-api` | elevated gateway latency | origin appears Top-3 RCA |
| Error burst | `order-service` | elevated 5xx and retries | one correlated incident |
| Stale telemetry | telemetry backend | quality gate blocks scoring | incident marks degraded source |
| Trace backend outage | tempo | RCA confidence drops | workflow remains usable |
| Unsafe approval | viewer role | remediation rejected | audit records rejection |

## Current Deterministic Flow

```text
mongodb anomaly starts first
order-service shows latency and error symptoms
api-gateway shows downstream client errors
correlator merges all anomalies into one incident
RCA ranks mongodb first using temporal, dependency, trace, severity, and history evidence
recommendation returns investigation steps and a gated demo action
```

