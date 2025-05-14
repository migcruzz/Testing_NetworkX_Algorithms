from pathlib import Path
from typing import List, Union
import pandas as pd

# Generic column names (adjust according to your CSV)
COL_SOURCE: str = "origin"
COL_TARGET: str = "destination"
COL_ATTR1: str = "attr1"
COL_ATTR2: str = "attr2"
COL_ATTR3: str = "attr3"
COL_RESULT: str = "combined_cost"

class CSVLinearCombiner:
    """
    Reads an edge list CSV with generic columns:
      - COL_SOURCE (e.g., 'origin')
      - COL_TARGET (e.g., 'destination')
      - COL_ATTR1, COL_ATTR2, COL_ATTR3 (attributes to combine)
    and adds a new column COL_RESULT = w0*attr1 + w1*attr2 + w2*attr3.
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        weights: List[float],
        encoding: str = 'utf-8'
    ) -> None:
        self.file_path = Path(file_path)
        self.encoding = encoding

        if len(weights) != 3:
            raise ValueError("Exactly 3 weights are required for linear combination.")
        self.weights = weights

    def process(self) -> pd.DataFrame:
        df = pd.read_csv(self.file_path, encoding=self.encoding)

        required = {COL_SOURCE, COL_TARGET, COL_ATTR1, COL_ATTR2, COL_ATTR3}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Missing columns in CSV: {missing}")

        w0, w1, w2 = self.weights
        df[COL_RESULT] = (
            w0 * df[COL_ATTR1]
            + w1 * df[COL_ATTR2]
            + w2 * df[COL_ATTR3]
        )
        return df

    def to_csv(self) -> str:
        """
        Returns the full CSV (including COL_RESULT) as a string without index.
        """
        return self.process().to_csv(index=False)

"""
# Usage example:
if __name__ == '__main__':
    combiner = CSVLinearCombiner(
        file_path=Path('edges.csv'),
        weights=[0.5, 0.3, 0.2],  # [w0, w1, w2]
        encoding='utf-8'
    )
    df_out = combiner.process()
    print(df_out.head())

"""

