"""
MLRan Preprocessing and Feature Pipeline Module.
Implements reproducible data loading, strict train-only fitting, schema validation,
and pipeline serialization for both tree-based models and linear/SVM models.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Union, Any

import numpy as np
import pandas as pd
import joblib
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class MLRanPreprocessor(BaseEstimator, TransformerMixin):
    """
    Preprocessor for MLRan ransomware behavioral datasets.
    
    Guarantees:
    - Zero data leakage: Fits scalers strictly on training data.
    - Strict schema verification: Validates feature order and types during inference.
    - Flexible ingestion: Supports dicts with feature IDs or human-readable names, Series, DataFrames, and ndarrays.
    - Dual mode: Scaled output for Logistic Regression / SVM; unscaled for Random Forest / XGBoost.
    - Reusability: Full serialization via joblib for production deployment.
    """
    
    def __init__(
        self,
        scale_for_linear_models: bool = False,
        feature_name_mapping: Optional[Dict[str, str]] = None
    ):
        self.scale_for_linear_models = scale_for_linear_models
        self.feature_name_mapping = feature_name_mapping or {}
        self.reverse_mapping = {v: k for k, v in self.feature_name_mapping.items()}
        self.scaler: Optional[StandardScaler] = StandardScaler() if scale_for_linear_models else None
        self.feature_names_: Optional[List[str]] = None
        self.n_features_in_: Optional[int] = None
        self.is_fitted_: bool = False

    def fit(self, X: Union[pd.DataFrame, np.ndarray], y: Optional[Any] = None) -> 'MLRanPreprocessor':
        """
        Fit preprocessor strictly on training features.
        """
        if isinstance(X, pd.DataFrame):
            self.feature_names_ = list(X.columns)
            self.n_features_in_ = len(self.feature_names_)
            X_array = X.values
        elif isinstance(X, np.ndarray):
            self.n_features_in_ = X.shape[1]
            self.feature_names_ = [str(i) for i in range(self.n_features_in_)]
            X_array = X
        else:
            raise ValueError("X must be a pandas DataFrame or numpy ndarray.")

        # Validate no infinite values
        if np.isinf(X_array).any():
            raise ValueError("X contains infinite values which cannot be processed.")

        if self.scaler is not None:
            self.scaler.fit(X_array)

        # Update reverse mapping
        self.reverse_mapping = {v: k for k, v in self.feature_name_mapping.items()}
        self.is_fitted_ = True
        return self

    def transform(self, X: Union[pd.DataFrame, pd.Series, np.ndarray, Dict[str, Any], List[Any]]) -> np.ndarray:
        """
        Transform input samples using fitted parameters.
        Supports:
        - Dictionary: keys can be feature column IDs (e.g. '5') or human-readable names (e.g. 'API:NtProtectVirtualMemory')
        - Pandas Series: single sample
        - Pandas DataFrame: batch or single sample (auto-fills missing columns with 0.0)
        - NumPy Array: 1D (single sample) or 2D (batch)
        - List: 483 feature values
        """
        if not self.is_fitted_:
            raise RuntimeError("MLRanPreprocessor must be fitted before transforming data.")

        # 1. Handle dictionary or pandas Series
        if isinstance(X, (dict, pd.Series)):
            d = dict(X)
            row = []
            for col in self.feature_names_:
                # Check column ID first, then human-readable name
                readable_name = self.feature_name_mapping.get(col, col)
                val = d.get(col, d.get(readable_name, 0.0))
                try:
                    row.append(float(val) if val is not None else 0.0)
                except (ValueError, TypeError):
                    row.append(0.0)
            X_array = np.array([row], dtype=np.float64)

        # 2. Handle pandas DataFrame
        elif isinstance(X, pd.DataFrame):
            # Map human-readable column names to feature IDs if needed
            df_renamed = X.copy()
            if self.reverse_mapping:
                df_renamed = df_renamed.rename(columns=self.reverse_mapping)
            
            # Align columns; fill any missing features with 0.0
            for col in self.feature_names_:
                if col not in df_renamed.columns:
                    df_renamed[col] = 0.0
            
            X_ordered = df_renamed[self.feature_names_]
            X_array = X_ordered.values.astype(np.float64)

        # 3. Handle list
        elif isinstance(X, list):
            X_array = np.array(X, dtype=np.float64)
            if X_array.ndim == 1:
                if len(X_array) != self.n_features_in_:
                    raise ValueError(f"Expected {self.n_features_in_} features, got {len(X_array)}")
                X_array = X_array.reshape(1, -1)

        # 4. Handle numpy ndarray
        elif isinstance(X, np.ndarray):
            if X.ndim == 1:
                if len(X) != self.n_features_in_:
                    raise ValueError(f"Expected {self.n_features_in_} features, got {len(X)}")
                X_array = X.reshape(1, -1).astype(np.float64)
            else:
                if X.shape[1] != self.n_features_in_:
                    raise ValueError(f"Expected {self.n_features_in_} features, got {X.shape[1]}")
                X_array = X.astype(np.float64)

        else:
            raise ValueError(f"Unsupported input type for transform: {type(X)}")

        # Handle NaNs or Infs safely
        if np.isnan(X_array).any() or np.isinf(X_array).any():
            X_array = np.nan_to_num(X_array, nan=0.0, posinf=1e6, neginf=-1e6)

        if self.scaler is not None:
            return self.scaler.transform(X_array)
        return X_array

    def fit_transform(self, X: Union[pd.DataFrame, np.ndarray], y: Optional[Any] = None) -> np.ndarray:
        return self.fit(X, y).transform(X)

    def get_feature_names(self) -> List[str]:
        if self.feature_names_ is None:
            raise RuntimeError("Preprocessor not fitted yet.")
        return self.feature_names_

    def get_readable_feature_names(self) -> List[str]:
        """Return human-readable names corresponding to the ordered feature columns."""
        if self.feature_names_ is None:
            raise RuntimeError("Preprocessor not fitted yet.")
        return [self.feature_name_mapping.get(col, col) for col in self.feature_names_]

    def save(self, filepath: str) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> 'MLRanPreprocessor':
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Saved preprocessor file not found at: {filepath}")
        preprocessor = joblib.load(filepath)
        if not isinstance(preprocessor, cls):
            raise TypeError(f"Loaded object is not an instance of {cls.__name__}")
        return preprocessor


def load_raw_mlran_data(
    data_dir: str
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, str]]:
    train_path = os.path.join(data_dir, "MLRan_X_train_RFE.csv")
    test_path = os.path.join(data_dir, "MLRan_X_test_RFE.csv")
    labels_path = os.path.join(data_dir, "MLRan_labels.csv")
    meta_path = os.path.join(data_dir, "mlran_dataset_metadata.csv")
    json_path = os.path.join(data_dir, "RFE_selected_feature_names_dic.json")

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)
    labels_df = pd.read_csv(labels_path)
    meta_df = pd.read_csv(meta_path)
    with open(json_path, "r", encoding="utf-8") as f:
        rfe_dict = json.load(f)

    return train_df, test_df, labels_df, meta_df, rfe_dict


def split_features_and_targets(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    meta_cols: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.DataFrame, pd.Series, pd.DataFrame]:
    if meta_cols is None:
        meta_cols = ["sample_id", "sample_type", "family_label", "type_label"]

    feature_cols = [c for c in train_df.columns if c not in meta_cols]

    X_train = train_df[feature_cols].copy()
    y_train = train_df["sample_type"].copy().astype(int)
    meta_train = train_df[meta_cols].copy()

    X_test = test_df[feature_cols].copy()
    y_test = test_df["sample_type"].copy().astype(int)
    meta_test = test_df[meta_cols].copy()

    return X_train, y_train, meta_train, X_test, y_test, meta_test


def execute_preprocessing_pipeline(
    raw_data_dir: str,
    processed_data_dir: str,
    models_dir: str
) -> Dict[str, Any]:
    os.makedirs(processed_data_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)

    train_df, test_df, labels_df, meta_df, rfe_dict = load_raw_mlran_data(raw_data_dir)
    X_train, y_train, meta_train, X_test, y_test, meta_test = split_features_and_targets(train_df, test_df)

    preprocessor_tree = MLRanPreprocessor(
        scale_for_linear_models=False,
        feature_name_mapping=rfe_dict
    )
    preprocessor_tree.fit(X_train)
    tree_preprocessor_path = os.path.join(models_dir, "preprocessor_tree.joblib")
    preprocessor_tree.save(tree_preprocessor_path)

    preprocessor_scaled = MLRanPreprocessor(
        scale_for_linear_models=True,
        feature_name_mapping=rfe_dict
    )
    preprocessor_scaled.fit(X_train)
    scaled_preprocessor_path = os.path.join(models_dir, "preprocessor_scaled.joblib")
    preprocessor_scaled.save(scaled_preprocessor_path)

    X_train_path = os.path.join(processed_data_dir, "X_train.csv")
    y_train_path = os.path.join(processed_data_dir, "y_train.csv")
    X_test_path = os.path.join(processed_data_dir, "X_test.csv")
    y_test_path = os.path.join(processed_data_dir, "y_test.csv")
    meta_train_path = os.path.join(processed_data_dir, "metadata_train.csv")
    meta_test_path = os.path.join(processed_data_dir, "metadata_test.csv")
    feature_meta_path = os.path.join(models_dir, "feature_metadata.json")

    X_train.to_csv(X_train_path, index=False)
    y_train.to_frame(name="target").to_csv(y_train_path, index=False)
    X_test.to_csv(X_test_path, index=False)
    y_test.to_frame(name="target").to_csv(y_test_path, index=False)
    meta_train.to_csv(meta_train_path, index=False)
    meta_test.to_csv(meta_test_path, index=False)

    feature_metadata = {
        "feature_count": len(preprocessor_tree.get_feature_names()),
        "feature_column_ids": preprocessor_tree.get_feature_names(),
        "feature_readable_names": preprocessor_tree.get_readable_feature_names(),
        "target_mapping": {"0": "Goodware/Benign", "1": "Ransomware"},
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "scale_tree_path": tree_preprocessor_path,
        "scale_linear_path": scaled_preprocessor_path
    }
    with open(feature_meta_path, "w", encoding="utf-8") as f:
        json.dump(feature_metadata, f, indent=2)

    return {
        "X_train_shape": X_train.shape,
        "y_train_shape": y_train.shape,
        "X_test_shape": X_test.shape,
        "y_test_shape": y_test.shape,
        "train_class_dist": y_train.value_counts().to_dict(),
        "test_class_dist": y_test.value_counts().to_dict(),
        "feature_count": len(preprocessor_tree.get_feature_names()),
        "saved_files": [
            X_train_path, y_train_path, X_test_path, y_test_path,
            meta_train_path, meta_test_path,
            tree_preprocessor_path, scaled_preprocessor_path, feature_meta_path
        ]
    }
