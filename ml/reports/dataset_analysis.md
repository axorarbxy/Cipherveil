# Multi-Dataset Research & Comparative Analysis Report

## Ransomware Early-Warning System for Small Institutions (SIH CYB04)

---

### Executive Summary

To establish comprehensive ransomware early-warning defense across multiple telemetry layers (Endpoint Runtime, Storage Block I/O, Shared Memory, and Enterprise Active Directory), four prominent public datasets were researched, analyzed, and evaluated:

1. **MLRan** (Baseline): 483-dimensional runtime dynamic behavioral features across 4,880 malware and benign executions.
2. **Active Directory Early-Stage Dataset (UMBC DREAM Lab)**: Sysmon and Windows Security Event Logs during the initial 20–25 minutes of lateral staging.
3. **RanSAP**: Hypervisor-level raw block storage I/O access patterns and block entropy streams.
4. **RanSMAP**: Multitasking storage access patterns combined with memory bus telemetry.

---

### Dataset Comparison Matrix

| Dimension | MLRan (Core Baseline) | Active Directory Early-Stage | RanSAP | RanSMAP |
| :--- | :--- | :--- | :--- | :--- |
| **Telemetry Level** | Host Userland & Sandbox API | Enterprise Domain Controller / Host Logs | Hypervisor Storage (Block I/O) | Hypervisor Storage + Memory |
| **Data Format** | Feature Vectors (CSV) | Windows Event Logs (CSV) | Raw Block Access Traces (CSV) | Multitasking Access Traces (CSV) |
| **Total Samples** | 4,880 samples | 122,180 security events | ~150,000 block events | ~200,000 block/memory events |
| **Label Granularity** | Binary per Executable (0/1) | Event Log Streams (Attack vs Normal) | Per Application / Family Run | Per Multitasking Run |
| **Benign Coverage** | 2,550 Benign Software | Normal Domain Operations (Before-Attack) | Office, Browsers, AESCrypt | Concurrent Benign Tasks |
| **Ransomware Families** | 64 Families (WannaCry, Locky, etc.) | AD Lateral Deployment Ransomware | Cerber, Darkside, GandCrab, Locky | Ransomware + Normal Mix |
| **Key Indicators** | API, Registry, Drops, Signatures | EventID 4688, 4624, Sysmon 1, 3, 11 | LBA, Write Burst, Block Entropy | Storage Burst, Memory Heatmap |
| **ML Role** | **Primary Endpoint ML Model** | **Enterprise Event Early-Warning Engine** | **Storage Layer Feature Engine** | **Memory/Storage Anomaly Engine** |

---

### Technical Reason Against Naive Data Merging (`pd.concat`)

> [!WARNING]
> Blindly concatenating these datasets with `pd.concat([mlran, ransap, ransmap, ad])` is scientifically invalid and causes complete feature semantic collapse.

* **Semantic Incompatibility**: An entry in RanSAP is a single ATA disk write packet (`timestamp, lba, size, entropy`), whereas an entry in MLRan is a summary vector of an entire 5-minute sandbox run (`483 binary/numeric frequency counters`), and an entry in the AD dataset is an XML-derived Windows Event Log (`EventID 4688: Process Creation`).
* **Appropriate Multi-Dataset Architecture**:
  * Maintain **MLRan as the primary trained baseline** for endpoint runtime monitoring.
  * Extract domain-specific windowed features from RanSAP and AD datasets to train dedicated, complementary early-warning models.
  * Define a **Common Behavioral Representation Schema** (`models/feature_mapping.json`) mapping high-level system categories.
