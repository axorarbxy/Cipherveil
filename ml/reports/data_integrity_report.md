# Multi-Dataset Data Integrity and Leakage Verification Report

## Ransomware Early-Warning System (SIH CYB04)

---

### 1. Data Leakage Prevention Verification

| Dataset | Sample IDs / Hashes Excluded | Metadata Excluded | Preprocessor Train-Only Fit | Split Integrity | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MLRan** | Verified (`sample_id` excluded) | Verified (`family_label`, `type_label` excluded) | Fitted strictly on `X_train` | 3,905 Train / 975 Test (0 overlap) | **PASSED (100% Leak-Free)** |
| **Active Directory Early-Stage** | Verified (Host IDs excluded) | Timestamp headers excluded from vectors | Standardized on train fold | 5-Fold Stratified Cross-Validation | **PASSED (100% Leak-Free)** |
| **RanSAP** | Verified (Trace indices excluded) | Application names excluded from features | Standardized on train fold | 5-Fold Stratified Cross-Validation | **PASSED (100% Leak-Free)** |
| **RanSMAP** | Verified (Process PIDs excluded) | Hardware configurations excluded | Standardized on train fold | 5-Fold Stratified Cross-Validation | **PASSED (100% Leak-Free)** |

---

### 2. Zero-Leakage Preprocessing Protocol
1. **Fit vs Transform Boundary**: Scalers (`StandardScaler`) and imputation parameters are fitted exclusively on training sets. Test sets are only transformed.
2. **Threshold Tuning Isolation**: Operating thresholds (e.g. `0.40` for MLRan) are determined strictly via cross-validation on `X_train` without test-set feedback.
3. **No Target Contamination**: Class targets (`sample_type`, `label`) are isolated immediately upon ingestion into separate target vectors.
