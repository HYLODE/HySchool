## Aim 

You are going to create your user own user page, and publish that to the HySchool website.

### Pre-requisites

- you have completed Lesson 1 (see `./noobie/lesson-1.md`)
- you have checked out the repository to tag **noobie-lesson-2**

You can do this from the command line (below) or using the GitHub Desktop app that you installed in Lesson 1.

```sh
git checkout noobie-lesson-2
```

### Lesson plan

1. Set-up 
2. Install Quarto (our documentation and website system) `<-- you are here`
3. Write and publish your first page

Please note that this **readme.md** file will change as we progress through the lessons. You will need to come back here after each step.

## Lesson 2: Install Quarto

First

- confirm you know where your repo is **Repository > Show in Finder** on your machine
- open VS Code and go to **File > Open Folder...** (or equivalent on Windows) and open the folder above

This lesson will show you how to get the HySchool website running on your own machine. To do this we need to run through the Quarto set-up process.

Go to [Quarto](https://quarto.org) and follow the [Get Started](https://quarto.org/docs/get-started/) instructions. We're going to assume you're using the [VS Code getting started tutorial](https://quarto.org/docs/get-started/hello/vscode.html).

You will also need to

- check you having a working Python installation
- Set-up a Python (or Conda) virtual environment (Optional but extra credit)
- install several extensions for VS Code including
  - the [Quarto extension](https://marketplace.visualstudio.com/items?itemName=quarto.quarto)
  - the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)


### Detour (possibly important)

- Installing [Python and Anaconda](https://carpentries.github.io/workshop-template/#python) or the DIY [Miniconda version](https://docs.conda.io/en/latest/miniconda.html)
- Working with Python in [VS Code](https://code.visualstudio.com/docs/languages/python)
  

## Quarto 'Hello World'

Go to your shell and install the necessary Python packages. They may already be there if you installed Anaconda.

```sh
python3 -m pip install jupyter matplotlib plotly_express
```

If you run into trouble you may need to quit and re-open VSCode and the Terminal to ensure that everything is properly configured.

You must use *python > select interpreter* in VSCode (see https://code.visualstudio.com/docs/python/environments#_select-and-activate-an-environment) else it will continue to default to the base setting and not run the Quarto preview etc commands using the right Python interpreter.
