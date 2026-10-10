"""
Top-level preprocessing module wrapper.
"""
import sys
import os

# Ensure package importability
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.preprocessing.preprocess_mlran import (
    MLRanPreprocessor,
    load_raw_mlran_data,
    split_features_and_targets,
    execute_preprocessing_pipeline
)

__all__ = [
    "MLRanPreprocessor",
    "load_raw_mlran_data",
    "split_features_and_targets",
    "execute_preprocessing_pipeline"
]
