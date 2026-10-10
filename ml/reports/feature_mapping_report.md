# Common Behavioral Feature Mapping & Telemetry Taxonomy

## Cross-Dataset Alignment (MLRan, RanSAP, RanSMAP, AD Early-Stage)

---

### Unified Behavioral Taxonomy

| Common Category | MLRan Telemetry Layer | Active Directory Enterprise Layer | RanSAP Hypervisor Layer | RanSMAP Layer |
| :--- | :--- | :--- | :--- | :--- |
| **FILE_OPERATIONS** | 16 File API features, dropped extensions | Sysmon Event 11, EventID 4663 | ATA write rate, sector count | Write I/O bandwidth |
| **STORAGE_ENTROPY** | RWX signatures, encrypted staging | File stream creation hashes | Block Shannon entropy ($>7.5$) | Memory/disk entropy |
| **PROCESS_ACTIVITY** | 63 API features, thread injection | EventID 4688 (Process spawn) | Indirect (I/O initiator) | Memory bus hotspots |
| **SYSTEM_REGISTRY** | 90 Registry read/write keys | EventID 4657 (Registry changes) | Volume metadata writes | Metadata updates |
| **NETWORK_LATERAL** | Socket APIs, C2 IP strings | EventID 4624 (Logon 3), 5140 (Share) | None (Isolated storage) | None |

---

### Operational Integration Guidelines
1. **Endpoint Protection**: Use the **MLRan XGBoost detector** for local agent process & API anomaly scoring.
2. **Enterprise Domain Controller**: Use **AD Early-Stage Event Log modeling** to catch lateral movement before payload execution.
3. **Storage Subsystem**: Use **RanSAP entropy & burst thresholds** to identify bulk file overwrites independently of the OS kernel.
