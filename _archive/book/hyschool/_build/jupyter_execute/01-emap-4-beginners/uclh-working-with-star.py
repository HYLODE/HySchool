#!/usr/bin/env python
# coding: utf-8

# # Working with EMAP star

# A template JupyterNotebook for working with EMAP. The following features of this notebook, and associated files are documented here to minimise the risk of data leaks or other incidents.
# 
# - Usernames and passwords are stored in a .env file that is excluded from version control. The example `env` file at `./config/env` should be edited and saved as `./config/.env`. A utility function `load_env_vars()` is provided that will confirm this file exists and load the configuration into the working environment.
# - .gitattributes are set to strip JupyterNotebook cells when pushing to GitHub

# ## Basic set-up

# Load libraries

# In[ ]:


import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pathlib import Path
from sqlalchemy import create_engine


# In[ ]:


from utils.setup import load_env_vars


# ## Load environment variables
# 
# Load environment variables and set-up SQLAlchemy connection engine for the EMAP Star

# In[ ]:


# Load environment variables
load_env_vars()

# Construct the PostgreSQL connection
uds_host = os.getenv('EMAP_DB_HOST')
uds_name = os.getenv('EMAP_DB_NAME')
uds_port = os.getenv('EMAP_DB_PORT')
uds_user = os.getenv('EMAP_DB_USER')
uds_passwd = os.getenv('EMAP_DB_PASSWORD')

emapdb_engine = create_engine(f'postgresql://{uds_user}:{uds_passwd}@{uds_host}:{uds_port}/{uds_name}')


# The above code is also abstracted into a function (below) but shown in long form above to make clear what we are doing.
# ```python
# from utils.setup import make_emap_engine
# emapdb_engine = make_emap_engine
# ```

# ## A first example script
# 
# Now use the connection to work with EMAP.
# 
# For example, let's inspect patients currently in ED or Resus.
# 
# Here's the SQL:
# 
# ```sql
# -- Example script 
# -- to pick out patients currently in A&E resus or majors
# 
# SELECT
#    vd.location_visit_id
#   ,vd.hospital_visit_id
#   ,vd.location_id
#   -- ugly HL7 location string 
#   ,lo.location_string
#   -- time admitted to that bed/theatre/scan etc.
#   ,vd.admission_time
#   -- time discharged from that bed
#   ,vd.discharge_time
# 
# FROM star.location_visit vd
# -- location label
# INNER JOIN star.location lo ON vd.location_id = lo.location_id
# WHERE 
# -- last few hours
# vd.admission_time > NOW() - '12 HOURS'::INTERVAL	
# -- just CURRENT patients
# AND
# vd.discharge_time IS NULL
# -- filter out just ED and Resus or Majors
# AND
# -- unpacking the HL7 string formatted as 
# -- Department^Ward^Bed string
# SPLIT_PART(lo.location_string,'^',1) = 'ED'
# AND
# SPLIT_PART(lo.location_string,'^',2) ~ '(RESUS|MAJORS)'
# -- sort
# ORDER BY lo.location_string
# ;
# 
# ```
# 

# The SQL script is stored at `../snippets/sql-vignettes/current_bed.sql`.\
# We can load the script, and read the results into a Pandas dataframe.
# 

# In[ ]:


# Read the sql file into a query 'q' and the query into a dataframe
q = Path('../snippets/sql-vignettes/current_bed.sql').read_text()
df = pd.read_sql_query(q, emapdb_engine)


# In[ ]:


df.head()


# ## Working with hospital visits
# 
# A series of three scripts
# 
# 1. Simply pull hospital visits
# 2. Add in hospital numbers (MRN) and handle patient merges
# 3. Add in patient demographics

# ### Simply pull hospital visits
# 
# ```sql
# SELECT
#    vo.hospital_visit_id
#   ,vo.encounter
#   -- admission to hospital
#   ,vo.admission_time
#   ,vo.arrival_method
#   ,vo.presentation_time
#   -- discharge from hospital
#   -- NB: Outpatients have admission events but not discharge events
#   ,vo.discharge_time
#   ,vo.discharge_disposition
# 
# -- start from hospital visits
# FROM star.hospital_visit vo
# WHERE 
#       -- hospital visits within the last 12 hours
#       vo.presentation_time > NOW() - '12 HOURS'::INTERVAL	
#       -- emergencies
#   AND vo.patient_class = 'EMERGENCY'
#       -- attending via ambulance
#   AND vo.arrival_method = 'Ambulance'
#       -- sort descending
# ORDER BY vo.presentation_time DESC
# ; 
# ```

# In[ ]:


# Read the sql file into a query 'q' and the query into a dataframe
q = Path('../snippets/sql-vignettes/hospital_visit_1.sql').read_text()
df = pd.read_sql_query(q, emapdb_engine)

df.head()


# ### Add in hospital numbers (MRN) and handle patient merges
# 
# See the series of joins in the middle of the script that retrieve the live MRN.
# That is we recognise that patients may have had an episode of care with one MRN, and then that episode was merged with another historical MRN. One of those two MRNs will then become the 'live' MRN and can be used to trace the patient across what otherwise would be different identities.
# 
# ```sql
# SELECT
#    vo.hospital_visit_id
#   ,vo.encounter
#   ,vo.admission_time
#   ,vo.arrival_method
#   ,vo.presentation_time
#   ,vo.discharge_time
#   ,vo.discharge_disposition
#   -- original MRN
#   ,original_mrn.mrn AS original_mrn
#   -- live MRN
#   ,live_mrn.mrn AS live_mrn
# 
# -- start from hospital visits
# FROM star.hospital_visit vo
# -- get original mrn
# INNER JOIN star.mrn original_mrn ON vo.mrn_id = original_mrn.mrn_id
# -- get mrn to live mapping 
# INNER JOIN star.mrn_to_live mtl ON vo.mrn_id = mtl.mrn_id 
# -- get live mrn 
# INNER JOIN star.mrn live_mrn ON mtl.live_mrn_id = live_mrn.mrn_id 
# 
# WHERE 
#       -- hospital visits within the last 12 hours
#       vo.presentation_time > NOW() - '12 HOURS'::INTERVAL	
#       -- emergencies
#   AND vo.patient_class = 'EMERGENCY'
#       -- attending via ambulance
#   AND vo.arrival_method = 'Ambulance'
#       -- sort descending
# ORDER BY vo.presentation_time DESC
# ; 
# ```

# In[ ]:


# Read the sql file into a query 'q' and the query into a dataframe
q = Path('../snippets/sql-vignettes/hospital_visit_2.sql').read_text()
df = pd.read_sql_query(q, emapdb_engine)

df.head()


# ### Add in patient demographics 
# 
# ```sql
# SELECT
#    vo.hospital_visit_id
#   ,vo.encounter
#   ,vo.admission_time
#   ,vo.arrival_method
#   ,vo.presentation_time
#   ,vo.discharge_time
#   ,vo.discharge_disposition
#   -- original MRN
#   ,original_mrn.mrn AS original_mrn
#   -- live MRN
#   ,live_mrn.mrn AS live_mrn
# 
#   -- core demographics
#   ,cd.date_of_birth
#   -- convert dob to age in years
#   ,date_part('year', AGE(cd.date_of_birth)) AS age
#   ,cd.sex
#   ,cd.home_postcode
#   -- grab initials from first and last name
#   ,CONCAT(LEFT(cd.firstname, 1), LEFT(cd.lastname, 1)) AS initials
# 
# -- start from hospital visits
# FROM star.hospital_visit vo
# INNER JOIN star.core_demographic cd ON vo.mrn_id = cd.mrn_id
# 
# -- get original mrn
# INNER JOIN star.mrn original_mrn ON vo.mrn_id = original_mrn.mrn_id
# -- get mrn to live mapping 
# INNER JOIN star.mrn_to_live mtl ON vo.mrn_id = mtl.mrn_id 
# -- get live mrn 
# INNER JOIN star.mrn live_mrn ON mtl.live_mrn_id = live_mrn.mrn_id 
# 
# WHERE 
#       -- hospital visits within the last 12 hours
#       vo.presentation_time > NOW() - '12 HOURS'::INTERVAL	
#       -- emergencies
#   AND vo.patient_class = 'EMERGENCY'
#       -- attending via ambulance
#   AND vo.arrival_method = 'Ambulance'
#       -- sort descending
# ORDER BY vo.presentation_time DESC
# ; 
# ```

# In[ ]:


# Read the sql file into a query 'q' and the query into a dataframe
q = Path('../snippets/sql-vignettes/hospital_visit_3.sql').read_text()
df = pd.read_sql_query(q, emapdb_engine)

df.head()


# ## Working with observations
# 
# WIP: example script to work with vitals

# ```sql
# -- Example script showing how to work with observations
# 
# -- V simple view that finds recent observations 
# -- for current inpatients in the last few minutes
# 
# 
# SELECT
#   -- observation details
#    ob.visit_observation_id
#   ,ob.hospital_visit_id
#   ,ob.observation_datetime
# 
#   --,ob.visit_observation_type_id
#   --,ot.id_in_application
# 
#   -- label nicely
#   ,CASE 
#     WHEN ot.id_in_application = '10' THEN 'SpO2'
#     WHEN ot.id_in_application = '5' THEN 'BP'
#     WHEN ot.id_in_application = '3040109304' THEN 'Oxygen'
#     WHEN ot.id_in_application = '6' THEN 'Temp'
#     WHEN ot.id_in_application = '8' THEN 'Pulse'
#     WHEN ot.id_in_application = '9' THEN 'Resp'
#     WHEN ot.id_in_application = '6466' THEN 'AVPU'
# 
#   END AS vital
# 
#   ,ob.value_as_real
#   ,ob.value_as_text
#   ,ob.unit 
#   
# FROM
#   star.visit_observation ob
# -- observation look-up
# LEFT JOIN
#   star.visit_observation_type ot
#   on ob.visit_observation_type_id = ot.visit_observation_type_id
# 
# WHERE
# ob.observation_datetime > NOW() - '5 MINS'::INTERVAL	
# AND
# ot.id_in_application in 
# 
#   (
#   '10'            --'SpO2'                  -- 602063230
#   ,'5'            --'BP'                    -- 602063234
#   ,'3040109304'   --'Room Air or Oxygen'    -- 602063268
#   ,'6'            --'Temp'                  -- 602063248
#   ,'8'            --'Pulse'                 -- 602063237
#   ,'9'            --'Resp'                  -- 602063257
#   ,'6466'         -- Level of consciousness
# )
# ORDER BY ob.observation_datetime DESC
# ;
# ```

# In[ ]:


# Read the sql file into a query 'q' and the query into a dataframe
q = Path('../snippets/sql-vignettes/vital_signs.sql').read_text()
df = pd.read_sql_query(q, emapdb_engine)

df.head()


# Now let's drill down on just heart rate

# In[ ]:


# Read the sql file into a query 'q' and the query into a dataframe
q = Path('../snippets/sql-vignettes/heart_rate.sql').read_text()
df = pd.read_sql_query(q, emapdb_engine)

df.head()


# In[ ]:


import plotly.express as px
figx = px.histogram(df, 
                    x='value_as_real',
                    title='Heart rate distribution at UCLH in the last 24 hours',
                   labels={'value_as_real': 'Heart Rate'})
figx.show()


# In[ ]:


# end of notebook


# In[ ]:




