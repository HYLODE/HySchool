from hyflow.fetch.icu.icu_episode_slices import icu_episode_slices_from_emap

??icu_episode_slices_from_emap

from hyflow.fetch.icu.icu_episode_slices import _icu_location_visits_from_emap

??_icu_location_visits_from_emap

from hygear.transform.cog1.icu_temporal import AdmissionAgeTransformer

AdmissionAgeTransformer??

from datetime import datetime, timedelta
import os
from pathlib import Path
from pprint import pprint
import urllib

import arrow
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sqlalchemy import create_engine

from hylib.dt import LONDON_TZ, convert_dt_columns_to_london_tz

ward = 'T03'

os.environ['EMAP_DB_USER'], os.environ['EMAP_DB_PASSWORD'] = Path('../secret').read_text().strip().split('\n')

uds_host = os.getenv('EMAP_DB_HOST')
uds_name = os.getenv('EMAP_DB_NAME')
uds_port = os.getenv('EMAP_DB_PORT')
uds_user = os.getenv('EMAP_DB_USER')
uds_passwd = os.getenv('EMAP_DB_PASSWORD')

emapdb_engine = create_engine(f'postgresql://{uds_user}:{uds_passwd}@{uds_host}:{uds_port}/{uds_name}')

from hyflow.settings import SQL_DIR
visits_sql = (SQL_DIR / "emap__icu_location_visit_history.sql").read_text()

# the point-in-time we are interested in:  7am on 17/07/2021 BST
horizon_dt = datetime(2021, 7, 17, 7, 0, 0).astimezone(LONDON_TZ)

from hylib.load.hydef import beds_from_hydef
beds_df = beds_from_hydef(ward)

visits_df = pd.read_sql(
    visits_sql,
    emapdb_engine,
    params={"horizon_dt": horizon_dt, "locations": list(beds_df.hl7_location)},
)

visits_df.head()

from datetime import datetime
import logging

from fastapi import APIRouter

from hylib.load.hydef import icu_observation_types_from_hydef

from hyflow.load.icu.icu_episode_slices import icu_episode_slices_from_hyflow
from hyflow.load.icu.icu_observations import icu_observations_from_hyflow
from hyflow.load.icu.icu_patients import icu_patients_from_hyflow

from hygear.transform.cog1.base import BaseCog1Transformer
from typing import List

class AdmissionAgeTransformer(BaseCog1Transformer):
    """
    An transformer for age at admission

    Output Features:
        `admission_age_years`: float
            Patient's age in years
    """

    input_cols = ["episode_slice_id", "admission_dt", "dob"]

    @property
    def output_cols(self) -> List[str]:
        return ["episode_slice_id", "admission_age_years"]

    def years(self, row: pd.Series) -> float:
        if pd.isnull(row.dob):
            return np.nan
        else:
            return int(row["admission_dt"].year) - int(row["dob"].year)

    def transform(self) -> pd.DataFrame:
        output_df = self.input_df

        output_df["admission_age_years"] = output_df.apply(self.years, axis=1)

        return output_df.loc[:, self.output_cols]

ward

horizon_dt = datetime(2021, 10, 12, 11, 00).astimezone(LONDON_TZ)

episode_slices_df = icu_episode_slices_from_hyflow(ward, horizon_dt)

episode_slices_df.shape

patients_df = icu_patients_from_hyflow(
    ward, horizon_dt, list(episode_slices_df.episode_slice_id)
)

age_input_df = episode_slices_df.loc[:, ["episode_slice_id", "admission_dt"]].join(
    patients_df.loc[:, ["episode_slice_id", "dob"]].set_index("episode_slice_id"),
    on="episode_slice_id",
)

age_df = AdmissionAgeTransformer(ward, horizon_dt, age_input_df).transform()
output_df = episode_slices_df.loc[:, ["episode_slice_id"]].join(
    age_df.set_index("episode_slice_id"), on="episode_slice_id"
)

age_df
