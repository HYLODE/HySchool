## Learning data science at UCLH

### Notes

Scope
- onboarding notes
- setting up your own local machine
- setting up for work at UCLH

### Training

Topics
- governance 
- safety
- git and version control
- data science for docs: r intro
- data science for docs: python intro

### Dev set-up

Contributing


# Lesson 2

- move to the next lesson
- confirm you know where your repo is **Repository > Show in Finder**
- open VS Code and go to **File > Open Folder...** and open the folder above
- this lesson will show you how to get the website running on your own machine
- we need to run through the Quarto set-up process


- go to [Quarto](https://quarto.org) and follow the [Get Started](https://quarto.org/docs/get-started/) instructions
- we're going to assume you're using the VS Code getting started tutorial
- note that skips over environment management (we should write a lesson for python environments)

- user is expected to install the quarto extension
- recommend the user to install the Python extension too https://marketplace.visualstudio.com/items?itemName=ms-python.python

- we may need to do a quick side lesson on the shell and python
- https://www.anaconda.com/products/distribution

- install when done will put the base conda environment into the path
- you get numpy etc for free
- reminder the user to logout and log back in to a fresh shell

```sh
python3 -m pip install jupyter matplotlib plotly_express
```

- could use the conda installer but prob need to add notes about adding the correct channel so for now stay with pip

- the user will need reminding to close and reopen vs code if conda was installed whilst going through the lesson else it won't see the right kernel
- then you must select the conda (base) kernel 
- this seems to be OK for the jupyter bits of vs code but quarto chokes
- looks like you have to do a fresh pip install for jupyter again (??)


- you must use python > select interpreter in vscode else it will continue to default to the base setting and not run the quarto preview etc commands using the right python