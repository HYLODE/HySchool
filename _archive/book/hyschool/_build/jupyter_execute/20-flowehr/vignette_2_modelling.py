from typing import List
import os
import tempfile
from pathlib import Path
import pickle
from uuid import uuid4
import datetime

import cloudpickle
import yaml
import pandas as pd
from matplotlib import pyplot as plt
import mlflow
from mlflow.tracking import MlflowClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import ParameterGrid, train_test_split
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, log_loss
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import NotFittedError
from sklearn.utils.validation import check_is_fitted
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.impute import MissingIndicator, SimpleImputer
from sklearn.pipeline import Pipeline as SKPipeline
from sklearn.preprocessing import (
    FunctionTransformer,
    OneHotEncoder,
    OrdinalEncoder,
    StandardScaler,
)

%matplotlib inline

from hylib.dt import LONDON_TZ
from hycastle.lens.base import BaseLens
from hycastle.lens.transformers import DateTimeExploder, timedelta_as_hours
from hycastle.lens.icu import BournvilleICUSitRepLens
from hycastle.icu_store.live import live_dataset
from hycastle.icu_store.retro import retro_dataset
from hymind.lib.models.icu_aggregate import AggregateDemandModel

# initialise MLFlow
mlflow_var = os.getenv('HYMIND_REPO_TRACKING_URI')
mlflow.set_tracking_uri(mlflow_var)   

client = MlflowClient()

df = retro_dataset('T03')

df.shape

df.head()

df.horizon_dt.min(), df.horizon_dt.max()

start_train_dt = datetime.datetime(2021,4,3,2,0,0).astimezone(LONDON_TZ)
end_train_dt = datetime.datetime(2021,6,30,23,0,0).astimezone(LONDON_TZ)

start_valid_dt = datetime.datetime(2021,7,1,1,0,0).astimezone(LONDON_TZ)
end_valid_dt = datetime.datetime(2021,7,31,23,0,0).astimezone(LONDON_TZ)

train_df = df[(start_train_dt < df['horizon_dt']) & (df['horizon_dt'] < end_train_dt)]
valid_df = df[(start_valid_dt < df['horizon_dt']) & (df['horizon_dt'] < end_valid_dt)]

train_df.head()

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
                # note we include then elapsed length of stay as a feature for our model,
                # as an alternative to training multiple models for different timepoints
                (
                    "elapsed_los_td_hrs",
                    FunctionTransformer(timedelta_as_hours),
                    ["elapsed_los_td"],
                ),
            ]
        )


# we start be instantiating the lens
lens = DemoLens()

# then we fit the lens on the training set, and transform that df
X_train = lens.fit_transform(train_df)

# similarly for the validation set, although here we only use transform(),
# as we have already fit the lens on train_df
X_valid = lens.transform(valid_df)

y_train = train_df['discharged_in_48hr'].astype(int)
y_valid = valid_df['discharged_in_48hr'].astype(int)

X_train.shape, y_train.shape, X_valid.shape, y_valid.shape

m = RandomForestClassifier(n_jobs=-1)
%time m.fit(X_train.values, y_train.values.ravel())

# Owner|Type|Name|Date e.g. 'TK|models|vignette|2021-11-22'
# n.b. if experiment name already exists, this cell with throw an error
#
# => add a unique experiment below <=
exp_name =


os.environ["MLFLOW_EXPERIMENT_NAME"] = exp_name
experiment_id = mlflow.create_experiment(exp_name)

experiment_id

tmp_path = Path('tmp')
tmp_path.mkdir(parents=True, exist_ok=True)

def mlflow_log_string(text, filename):
    full_path = tmp_path / filename
    with open(full_path, 'w') as f:
        f.write(str(text))
    mlflow.log_artifact(full_path)

def mlflow_log_tag_dict(tag_dict, filename):
    """Logs tag dict to MLflow (while preserving order unlike mlflow.log_dict)"""
    full_path = tmp_path / filename
    with open(full_path, 'w') as f:
        yaml.dump(tag_dict, f, sort_keys=False)
    mlflow.log_artifact(full_path)
    
def mlflow_log_lens(l):
    full_path = l.pickle(tmp_path)
    mlflow.log_artifact(full_path, 'lens')

tag_dict = {
    'start_train_dt': start_train_dt,
    'end_train_dt': end_train_dt,    
    'start_valid_dt': start_valid_dt,
    'end_valid_dt': end_valid_dt
}

with mlflow.start_run():
    mlflow_log_tag_dict(tag_dict, 'tag_dict.yaml')

# the two most influential parameters 
# cf. https://scikit-learn.org/stable/modules/ensemble.html#parameters
grid = {
    'n_estimators':[10, 50, 100],
    'max_features':[None, "sqrt", "log2"]
}

# as the outcome of each training run (even with the same parameters) is non-deterministic,
# we run two training runs per parameter combination.
runs_per_param_set = 2

for i in range(runs_per_param_set):
    
    for g in ParameterGrid(grid):
        m = RandomForestClassifier(n_jobs=-1)

        with mlflow.start_run():
            
            # logging the tag dictionary, the run_type
            mlflow_log_tag_dict(tag_dict, 'tag_dict.yaml')
            mlflow.set_tag("run_type", "training")
            
            # set and log this run's set of model parameters
            m.set_params(**g)
            mlflow.log_params(g)

            m.fit(X_train.values, y_train.values.ravel())
            
            # calculate and log training and validation set accuracy
            train_accuracy = m.score(X_train.values, y_train.to_numpy())
            mlflow.log_metric('train_accuracy', train_accuracy)
            valid_accuracy = m.score(X_valid.values, y_valid.to_numpy())       
            mlflow.log_metric('valid_accuracy', valid_accuracy)
            
            # ditto for confusion matrices
            train_confusion = confusion_matrix(m.predict(X_train.values), y_train.to_numpy())
            mlflow_log_string(train_confusion, 'train_confusion.txt')
            valid_confusion = confusion_matrix(m.predict(X_valid.values), y_valid.to_numpy())
            mlflow_log_string(valid_confusion, 'valid_confusion.txt')

            # store the trained SKLearn model, so we can check it out later
            mlflow.sklearn.log_model(m, 'model')

runs = mlflow.search_runs()
runs.head()

params = [col for col in runs if col.startswith('params')]
best_params = runs.groupby(params)['metrics.valid_accuracy'].mean().idxmax()
best_row = runs.set_index(keys=params).loc[best_params]

best_run_id = list(best_row['run_id'])[0]
best_run_id

with mlflow.start_run(run_id=best_run_id):
    # tag the run as best_row
    mlflow.set_tag('best_run', 1)   

    # log the lens
    mlflow_log_lens(lens)

# => add a unique model name below <=
# e.g. tk-random_forest-demo
model_name =

# n.b. each time you run this cell with the same model_name, the model version will increase by one
registered_model = mlflow.register_model(f'runs:/{best_run_id}/model', model_name)

# first off, we can surface basic info about the model using our model_name and version.

model_info = client.get_model_version(model_name, registered_model.version)
model_info

# we can then go deeper and inspect the run itself
run_info = client.get_run(model_info.run_id)
run_info

model = mlflow.sklearn.load_model(f'models:/{model_name}/{registered_model.version}')
model

with tempfile.TemporaryDirectory() as tmp:
    tmp_dir = Path(tmp)
    
    client.download_artifacts(model_info.run_id, 'lens', tmp_dir)
    
    lens_path = next((tmp_dir / 'lens').rglob('*.pkl'))
    with open(lens_path, 'rb') as f:
        loaded_lens = pickle.load(f)
        
loaded_lens

live_df = live_dataset('T03')
live_df.shape

# and inspecting the dataframe, note the most recent admission_dt
live_df.loc[:, ['episode_slice_id', 'admission_dt', 'bed_code', 'avg_heart_rate_1_24h']].sort_values('admission_dt', ascending=False).head()

# first we transform the live_df with our loaded_lens
X_df = loaded_lens.transform(live_df)
X_df.columns

# making the predictions
predictions = model.predict_proba(X_df.values)

# adding the predictions to our live_df dataframe
live_df['prediction'] = predictions[:, 1]
live_df.loc[:, ['episode_slice_id', 'prediction']].head()

AggregateDemandModel??

agg_demand = AggregateDemandModel()
agg_predictions = agg_demand.predict(context="", 
                                     model_input=live_df.loc[:, ['prediction']].rename(mapper={'prediction':'prediction_as_real'},axis=1))
agg_predictions.plot()

with tempfile.TemporaryDirectory() as tmp:
    tmp_dir = Path(tmp)
    
    client.download_artifacts(model_info.run_id, './', tmp_dir)
    
    tag_dict_path = tmp_dir / 'tag_dict.yaml'
    with open(tag_dict_path, 'r') as stream:
        loaded_tag_dict = yaml.load(stream, Loader=yaml.FullLoader)
        
loaded_tag_dict

loaded_valid_df = df[(loaded_tag_dict['start_valid_dt'] < df['horizon_dt']) &
                 (df['horizon_dt'] < loaded_tag_dict['end_valid_dt'])]

X_valid = loaded_lens.transform(loaded_valid_df)
y_valid = loaded_valid_df['discharged_in_48hr'].astype(int)

# then we have already loaded in our model in the previous section
model

with mlflow.start_run(run_id=best_run_id):
    
    mlflow_log_tag_dict(tag_dict, 'tag_dict.yaml')
    
    # create a 2-column dataframe of the predicted probabilities and true label,
    # for each patient in the validation set
    eval_df = pd.DataFrame({
                'predict_proba':model.predict_proba(X_valid.values)[:,1], 
                'label':y_valid.to_numpy().ravel()
               }, 
        columns=['predict_proba','label'],
        index=X_valid.index)   
    eval_df['horizon_dt'] = loaded_valid_df.set_index('episode_slice_id')['horizon_dt']
    
    # write eval_df to csv and log in MLFlow
    eval_path = tmp_path / 'eval.csv'
    eval_df.to_csv(eval_path)
    mlflow.log_artifact(eval_path)
    
    
    # use eval_df to store a new metric
    eval_log_loss = log_loss(eval_df['label'],eval_df['predict_proba'])
    mlflow.log_metric('log_loss', eval_log_loss)
    
    
    # save a new figure alongside our registered model
    eval_confusion = confusion_matrix(m.predict(X_valid.values), y_valid.to_numpy())
    disp = ConfusionMatrixDisplay(confusion_matrix=eval_confusion,
                              display_labels=['discharged','remained_after_48hrs'])
    
    confusion_path = tmp_path / 'confusion_fig_2.png'
    disp.plot(cmap=plt.cm.Blues).figure_.savefig(confusion_path)
    mlflow.log_artifact(confusion_path)


