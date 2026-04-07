import numpy as np
import pandas as pd
from typing import List, Optional, Tuple, Union
from imblearn.base import BaseSampler
from sklearn.base import TransformerMixin
from src.preprocessing.utils.normalization import NormalizerType, normalize
from src.preprocessing.utils.sampling import SamplerType, sample
from src.preprocessing.utils.target import TargetType, construct_targets


class DatasetPreprocessor:
    """ 
    Customized Dataset loader for Malebane.
    Added support for BTTS, Over/Under, and Corner tracking.
    """

    def __init__(self, drop_week: bool = True):
        # I REMOVED 'HC' and 'AC' from this list so the AI can now "see" corners!
        # I also removed 'HG' and 'AG' (Goals) so we can use them for BTTS/Overs.
        self._non_trainable_columns = ['Date', 'Season', 'Home', 'Away', 'Result', 'Result-U/O']

        if drop_week:
            self._non_trainable_columns.append('Week')

    @property
    def non_trainable_columns(self) -> List[str]:
        return self._non_trainable_columns

    def preprocess_dataset(
            self,
            df: pd.DataFrame,
            target_type: TargetType,
            normalizer: Optional[Union[NormalizerType, TransformerMixin]] = None,
            sampler: Optional[Union[SamplerType, BaseSampler]] = None,
            seed: Optional[int] = None
    ) -> Tuple[np.ndarray, np.ndarray, Optional[TransformerMixin]]:
        
        df = df.dropna().copy()

        # --- CUSTOM MALEBANE CALCULATIONS START ---
        # 1. BTTS (Both Teams to Score)
        if 'HG' in df.columns and 'AG' in df.columns:
            df['BTTS'] = ((df['HG'] > 0) & (df['AG'] > 0)).astype(int)
            
            # 2. Over 2.5 Goals
            df['Over_2_5'] = ((df['HG'] + df['AG']) > 2.5).astype(int)
            
            # 3. Exact Total Goals
            df['Total_Goals'] = df['HG'] + df['AG']
            
        # 4. Total Corners (Home Corners + Away Corners)
        if 'HC' in df.columns and 'AC' in df.columns:
            df['Total_Corners'] = df['HC'] + df['AC']
        # --- CUSTOM MALEBANE CALCULATIONS END ---

        # Construct inputs (The AI features)
        x = df.drop(columns=self._non_trainable_columns, errors='ignore').to_numpy(dtype=np.float32)

        # Construct targets (What we are trying to predict)
        y = construct_targets(df=df, target_type=target_type)

        # Apply input normalization and sampling.
        if normalizer is not None:
            x, normalizer = normalize(x=x, normalizer=normalizer)
        if sampler is not None:
            x, y, sampler = sample(x=x, y=y, sampler=sampler, seed=seed)

        # Validate sizes.
        if x.shape[0] != y.shape[0]:
            raise ValueError(f'Inconsistent sizes: {x.shape[0]} vs {y.shape[0]}')

        return x, y, normalizer
