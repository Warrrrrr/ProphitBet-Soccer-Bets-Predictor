import numpy as np
import pandas as pd
from enum import Enum
from sklearn.preprocessing import OneHotEncoder


class TargetType(Enum):
    """ 
    Expanded Target Types for Malebane's Goals.
    """
    RESULT = 'result'
    OVER_UNDER = 'over-under'
    BTTS = 'btts'
    EXACT_GOALS = 'exact-goals'
    CORNERS = 'corners'


def construct_targets(df: pd.DataFrame, target_type: TargetType) -> np.ndarray:
    """ Constructs the dataset targets based on the selected classification task """

    if target_type == TargetType.RESULT:
        y = df['Result'].replace({'H': 0, 'D': 1, 'A': 2}).to_numpy(dtype=np.int32)
    
    elif target_type == TargetType.OVER_UNDER:
        # Predicts if Total Goals >= 2.5
        y = ((df['HG'] + df['AG']).ge(2.5)).astype(np.int32).to_numpy()
        
    elif target_type == TargetType.BTTS:
        # Predicts if Both Teams Score (1 for Yes, 0 for No)
        y = ((df['HG'] > 0) & (df['AG'] > 0)).astype(np.int32).to_numpy()
        
    elif target_type == TargetType.EXACT_GOALS:
        # Predicts the exact number of goals (0, 1, 2, 3, 4, 5+)
        y = (df['HG'] + df['AG']).clip(upper=5).astype(np.int32).to_numpy()
        
    elif target_type == TargetType.CORNERS:
        # Predicts if Total Corners are High (e.g., > 9.5) or Low
        # We start with a 9.5 baseline, but this can be adjusted.
        y = ((df['HC'] + df['AC']).ge(9.5)).astype(np.int32).to_numpy()
        
    else:
        raise TypeError(f'Undefined target type: "{target_type.name}"')

    return y


def one_hot_encode(y: np.ndarray, target_type: TargetType) -> np.ndarray:
    """ One-Hot encodes the provided targets for Deep Learning models. """

    if target_type == TargetType.RESULT:
        categories = [[0, 1, 2]]
    elif target_type in [TargetType.OVER_UNDER, TargetType.BTTS, TargetType.CORNERS]:
        categories = [[0, 1]]
    elif target_type == TargetType.EXACT_GOALS:
        categories = [[0, 1, 2, 3, 4, 5]]
    else:
        raise TypeError(f'Not supported target type: "{target_type}"')

    return OneHotEncoder(categories=categories, sparse_output=False).fit_transform(y.reshape(-1, 1))
