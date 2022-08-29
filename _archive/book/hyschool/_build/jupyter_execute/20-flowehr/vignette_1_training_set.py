from hycastle.icu_store.retro import retro_dataset
from hycastle.icu_store.live import live_dataset # <-- includes PII

ward = 'T03'

# the retro_dataset function gives us all the historical episode slices to build up our training set
train_df = retro_dataset(ward)
train_df.shape

# and we can see the various feature columns we have generated
train_df.head()

predict_df = live_dataset(ward)
predict_df.shape

predict_df['horizon_dt'].head()

from hycastle.lens.base import BaseLens
from typing import List
from sklearn.compose import ColumnTransformer
from hycastle.lens.transformers import DateTimeExploder

class SimpleLens(BaseLens):
    numeric_output = True
    index_col = "episode_slice_id"

    @property
    def input_cols(self) -> List[str]:
        return [
            "episode_slice_id",
            "admission_dt",
        ]

    def specify(self) -> ColumnTransformer:
        return ColumnTransformer(
            [
                (
                    "select",
                    "passthrough",
                    [
                        "episode_slice_id"
                    ],
                ),
                (
                    "admission_dt_exp",
                    DateTimeExploder(),
                    ["admission_dt"],
                ),
            ]
        )

lens = SimpleLens()

X = lens.fit_transform(train_df)
X.head()

train_df['admission_dt'].head()

??DateTimeExploder

??DateTimeExploder.transform

from sklearn.preprocessing import (
    FunctionTransformer,
    OneHotEncoder,
    OrdinalEncoder,
    StandardScaler,
)
from sklearn.impute import MissingIndicator, SimpleImputer
from hycastle.lens.transformers import timedelta_as_hours

class DemoLens(BaseLens):
    numeric_output = True
    index_col = "episode_slice_id"

    @property
    def input_cols(self) -> List[str]:
        return [
            "episode_slice_id",
            "admission_age_years",
            "avg_heart_rate_1_24h",
            "max_temp_1_12h",
            "avg_resp_rate_1_24h",
            "elapsed_los_td",
            "admission_dt",
            "horizon_dt",
            "n_inotropes_1_4h",
            "wim_1",
            "bay_type",
            "sex",
            "vent_type_1_4h",
        ]

    def specify(self) -> ColumnTransformer:
        return ColumnTransformer(
            [
                (
                    "select",
                    "passthrough",
                    [
                        "episode_slice_id",
                        "admission_age_years",
                        "n_inotropes_1_4h",
                        "wim_1",
                    ],
                ),
                ("bay_type_enc", OneHotEncoder(), ["bay_type"]),
                (
                    "sex_enc",
                    OrdinalEncoder(
                        handle_unknown="use_encoded_value", unknown_value=-1
                    ),
                    ["sex"],
                ),
                (
                    "admission_dt_exp",
                    DateTimeExploder(),
                    ["admission_dt", "horizon_dt"],
                ),
                (
                    "vent_type_1_4h_enc",
                    OrdinalEncoder(
                        handle_unknown="use_encoded_value", unknown_value=-1
                    ),
                    ["vent_type_1_4h"],
                ),
                (
                    "vitals_impute",
                    SimpleImputer(strategy="mean", add_indicator=False),
                    [
                        "avg_heart_rate_1_24h",
                        "max_temp_1_12h",
                        "avg_resp_rate_1_24h",
                    ],
                ),
                (
                    "elapsed_los_td_hrs",
                    FunctionTransformer(timedelta_as_hours),
                    ["elapsed_los_td"],
                ),
            ]
        )

lens = DemoLens()

X = lens.fit_transform(train_df)
X.head()

X.dtypes


