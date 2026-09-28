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
                    f"Unsupported file format.\nSupported formats: CSV, XLSX, XLS."
                )

            # Strip column names to handle trailing whitespaces safely
            df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

            expected_columns = [
                "Number",
                "Caller",
                "Assignment Group",
                "Created",
                "Short description",
                "Category",
                "Priority",
                "State",
                "Assigned to",
                "Resolved by",
                "Resolved",
                "KB Number",
                "IT Batch Job",
                "Description",
                "Reassignment Count",
                "Configuration item",
                "Offending CI",
                "Offending CI Category"
            ]

            missing_columns = [col for col in expected_columns if col not in df.columns]

            if missing_columns:
                msg = (
                    "Missing columns:\n" + "\n".join(missing_columns) +
                    "\n\nExpected format:\n" + "\n".join(expected_columns)
                )
                raise ValueError(msg)

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