"""
Incident dataset loader.
"""

from pathlib import Path

import pandas as pd

from app.utils.logger import logger


class IncidentLoader:

    def __init__(self, filepath: str):

        self.filepath = filepath

    def load(self) -> pd.DataFrame:

        try:

            extension = Path(self.filepath).suffix.lower()

            if extension == ".csv":

                try:
                    df = pd.read_csv(self.filepath)
                except Exception:
                    logger.warning(
                        "Standard C parser failed for CSV; falling back to python engine with on_bad_lines='skip'."
                    )
                    df = pd.read_csv(self.filepath, on_bad_lines="skip", engine="python")

            elif extension in [".xlsx", ".xls"]:

                df = pd.read_excel(self.filepath)

            else:

                raise ValueError(
                    f"Unsupported file type: {extension}"
                )

            logger.info(
                "Loaded %s incidents.",
                len(df)
            )

            return df

        except Exception:

            logger.exception(
                "Failed to load dataset."
            )

            raise