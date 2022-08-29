#!/usr/bin/env python
# coding: utf-8

# # Vignette - end-to-end exemplar

# Let's begin an end-to-end modelling exemplar. The whole pipeline in c. 20 lines. In the previous section, we made some grand claims about Hylode addressing:
# 
#     ~ train-deploy split
#     ~ feature provision
#     ~ time-series modelling
#     ~ model management
#     ~ transition to deployment
#     
# Let's see a concrete example of how this looks.

# # Retrospective training set. Extraction & pre-processing

# For the sake of these notebooks, we're going to consider the problem of modelling ICU discharge at 48 hours.

# In[1]:


# First off, Hylode immediately gives us the features we need to train a time series model
from hycastle.icu_store.retro import retro_dataset

train_df = retro_dataset('T03')
train_df.shape


# This single piece of code has done a lot of work behind the scenes. 
# 
# It has pulled data from EMAP, processed it where necessary to create features and then cut those features up so we have one row per hour for each patient -- setting us up to make live predictions every hour for each patient on the unit.
# 
# Let's have a look at which features we have:

# In[ ]:


train_df.columns


# This is great, but we still have some categorical variables etc. laced in there. What happens if I want to do some pre-processing?
# 
# The answer lies in our `lens` abstraction, let's have a look at one I prepared earlier:

# In[ ]:


from hycastle.lens.icu import BournvilleICUSitRepLens
lens = BournvilleICUSitRepLens()

X_train = lens.fit_transform(train_df)
X_train.columns


# We can see we've just done some useful things. The lens's `fit_transform` method has inserted missingness values for ethnicity, and we have broken out each patient's admissions time into separate features as we think that will improve our model. 
# 
# We also define a label:

# In[ ]:


y_train = train_df['discharged_in_48hr'].astype(int)


# # Training & storing a model

# With this "heavy" lifting done, we should now already be in a position to train a model. Let's have a go:

# In[ ]:


from sklearn.ensemble import RandomForestClassifier
m = RandomForestClassifier(n_jobs=-1)
m.fit(X_train.values, y_train.values.ravel())


# Everything seems to be working. Let's imagine we're happy with what we've done. Let's log the model in our model repo, so it's primed and ready to deploy...

# In[ ]:


import os
import mlflow
mlflow_server = os.getenv('HYMIND_REPO_TRACKING_URI')
mlflow.set_tracking_uri(mlflow_server)


# In[ ]:


from datetime import datetime
import random
import string

# Generate a unique experiment name
exp_name = "vignette_0-" + "".join( random.sample(string.ascii_lowercase, k=8)) + str(datetime.now().timestamp())

os.environ["MLFLOW_EXPERIMENT_NAME"] = exp_name
experiment_id = mlflow.create_experiment(exp_name)

experiment_id


# In[ ]:


with mlflow.start_run():
    mlflow.sklearn.log_model(m, 'model')


# This [screenshot](MLFlow_screenshot.PNG) shows what it looks like for the model to land safely in MLFlow (which you should be able to see for yourself if you follow the link [here](http://uclvlddpragae08:5008/) -- look for a new experiment at the very bottom of the list on the left hand side)

# # Loading and deploying a model

# Now let's switch hats and imagine they were are trying to deploy the model in silent mode for the patients currently on the ICU. This is now pretty straightforward:

# In[ ]:


from hycastle.icu_store.live import live_dataset
live_df = live_dataset('T03')
live_df.shape


# In[ ]:


live_df.columns


# In[ ]:


X_df = lens.transform(live_df)


# In[ ]:


runs = mlflow.search_runs(experiment_ids=[experiment_id])
run_id = runs.iloc[0].run_id
run_id


# In[ ]:


logged_model = f'runs:/{run_id}/model'
loaded_model = mlflow.sklearn.load_model(logged_model)


# In[ ]:


predictions = loaded_model.predict_proba(X_df.values)
live_df['prediction'] = predictions[:, 1]
live_df.loc[:, ['bed_code', 'prediction']].head()


# In[ ]:




