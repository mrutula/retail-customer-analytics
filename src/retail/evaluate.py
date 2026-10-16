from pathlib import Path
import pandas as pd
from loguru import logger

# Locate the project root relative to this Python file
PROJECT_ROOT = Path(__file__).resolve().parents[2]

def log_results(results: dict) -> None:
    """
    Appends a row to results.csv for different models.

    Parameters
    ----------
    results : dict
        Contains the model name, log probabilities, and ROC-AUC score.

    Returns
    -------
    None
    """
    results_csv_path = PROJECT_ROOT / "data" / "results" / "results.csv"
    results_csv_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame([results])

    df.to_csv(
        results_csv_path,
        mode="a",
        header=not results_csv_path.exists(),
        index=False,
    )
