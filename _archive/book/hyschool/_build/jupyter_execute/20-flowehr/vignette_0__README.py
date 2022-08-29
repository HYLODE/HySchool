#!/usr/bin/env python
# coding: utf-8

# # Hi *(Hy?)* there... 

# Welcome to the Hylode platform. Thank you for making it this far.
# 
# Over the next four notebooks, we hope to bring you from zero to sixty on why we developed the platform and how to use it.
# 
# The backdrop to this infastructural work is a world where translating published EHR-driven ML4H models into deployment is hard. Reseachers internationally lament this implementation gap[<sup>1</sup>](#fn1). Even at UCLH, flush with a new EHR and live data infrastructure in EMAP, the last mile in pushing a retrospective model requires a lot of one-off project-specific work.
# 
# Intent on doing meaningful research and innovation in a safety critical environment - paving the way for live deployments - deployment needs to be taken more seriously. In particular, the deployment problems that the Hylode platform is looking to address include:
# 
# - __Risk of train-deploy split__, where discrepency between training and deployment code lower performance
# - __Data drift and feature drift__, where underlying shifts in the dataset harm performance unnoticed
# - __Ad hoc ongoing model monitoring and evaluation__, where continuous model scrutiny relies on ad hoc batch evaluation
#     
# We address these problem by presenting a single framework that:
#     
#     a) brings together training and deployment in the same modelling workflow
#     b) integrates MLOps modules addressing data drift, model evaluation etc. alongside the main platform
#     
# Rather than ad hoc algorithm deployment, Hylode is a platform for training deployable EHR models.

# # Case to the ML4H researcher...

# Does all this come at the expense of ease and speed for the ML researcher?
# 
# We hope not. Engineered into Hylode are abstractions crafted to make the specific kind of modelling EHR ML practitioners do easier, faster and more joyful. 
# 
# In particular:
# 
# - __Hylode provides a curated set of features__ easily interfacing w/ other UCLH data resources such as EMAP & Caboodle. Over time, we hope the store of pre-canned features will grow, cutting the time spent on wrangling, and freeing it up for more modelling work.
# - __Built for time-series EHR data__ Hylode automates many of the more fiddly elements of training a time-series ML4H model. It eases splitting patient records into temporal slices (the training instances needed to feed time-series EHR models).
# - __Ease of experimental logging & model development__ The Hylode system makes it easy to log results & create reproducible workflows. The same tooling then makes it straightforward to pass models over from ML teams to application developers, to then present the predictions in a clinically meaningful way.
#     
# We see these three strengths as coming together to make Hylode a central resource to develop deployable ML models at UCLH. The core driver here is that Hylode allows researchers to get their modelling done faster. 
# 
# From there, the deployment benefits of Hylode kick in. Starting from a single trained model, Hylode offers a seamless technical transition to running models in silent mode, and a clear path to application development and testing the real-time relevance of predictions in complex multi-disciplinary clinical settings.

# # The notebooks...

# Background over, we can now get started on the tutorial. The basic structure of these notebooks is as follows:
# 
# - [Notebook 0](vignette_0_intro.ipynb) A compact __end-to-end modelling exemplar__ evidencing the claims above in c. 20 lines of code.
#     
# From there, we switch to a more measured pace. The aim is to give the reader enough grounding to start working with the different system components themselves:
# 
# - [Notebook 1](vignette_1_training_set.ipynb) (__HyCastle__) More detail on feature access and preprocessing.
# - [Notebook 2](vignette_2_modelling.ipynb) (__HyMind__) A fuller end-to-end modelling platform exemplifying how we have been using the platform so far.
# - [Notebook 3](vignette_3_data_flow.ipynb) (Appendix - __HyFlow & HyGear__) For those interested, a delve under the hood. Here you can start triangulating yourself as to how the data is pulled from EMAP.

# ---

# <span id="fn1">1. Seneviratne, M. G., Shah, N. H. & Chu, L. Bridging the implementation gap of machine learning in healthcare. Bmj Innovations 6, 45 (2020).
#   </span>
