# Dataset Documentation — MLRan

## Ransomware Early-Warning System (Member 2 — ML Engineer)

### Dataset Overview
* **Dataset Name**: MLRan (Dynamic Behavioural Dataset for Ransomware Analysis and Detection)
* **Target Column**: `sample_type` (`0` = Goodware / Benign, `1` = Ransomware)
* **Dataset Partitions**:
  * **Training Set**: 3,905 samples (2,040 Goodware, 1,865 Ransomware)
  * **Test Set**: 975 samples (510 Goodware, 465 Ransomware)
* **Feature Count**: 483 behavioral ML features (API calls, Registry operations, File operations, Strings, Dropped files, Signatures).
* **Metadata Columns (Excluded from Features)**:
  * `sample_id` (Unique hash identifier)
  * `sample_type` (Binary target label: 0 or 1)
  * `family_label` (Specific ransomware family, e.g., WannaCry, Locky, Cerber)
  * `type_label` (High-level category)

---

### Expected File Placement
Place the raw dataset files inside `data/raw/MLRan/`:
```text
data/raw/MLRan/
├── MLRan_X_train_RFE.csv                 # 3,905 rows × 487 columns
├── MLRan_X_test_RFE.csv                  # 975 rows × 487 columns
├── MLRan_labels.csv                      # Complete label table
├── mlran_dataset_metadata.csv            # Detailed sample metadata
├── RFE_selected_feature_names_dic.json   # 483 feature IDs to readable descriptions
├── type_train_sampleids.csv              # Train split sample IDs
└── type_test_sampleids.csv               # Test split sample IDs
```

---

### How to Preprocess and Train
1. Run Preprocessing:
   ```bash
   python -c "from src.preprocessing.preprocess_mlran import execute_preprocessing_pipeline; execute_preprocessing_pipeline('data/raw/MLRan', 'data/processed', 'models')"
   ```
2. Train All Models:
   ```bash
   python src/train.py
   ```
3. Evaluate Models on Test Set:
   ```bash
   python src/evaluate.py
   ```
4. Run ML Verification Tests:
   ```bash
   python src/test_ml_module.py
   ```
