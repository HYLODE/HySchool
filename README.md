# EMAP at UCLH

See the accompanying [book](https://inform-health-informatics.github.io/emap-helper/intro.html)!

Repository for helper SQL, R & Python code to assist development on EMAP.
There are code snippets stored under `./snippets`.
Code should be separated in folders by topic

There is also a JupyterBook under production at `./book`. The main branch for working on the book is 'book'!. GitHub actions are set-up to automatically update the book and publish it whenever a new commit is pushed to the 'book' branch. The site is hosted from the 'gh-pages', but can be reached at https://inform-health-informatics.github.io/emap-helper/intro.html.

Advice on working with JupyterBook is available [here](https://jupyterbook.org/intro.html).

## Conventions
- With great power ... pushing from UCLH machines risks leaking data so .gitattributes is set to remove all notebook outputs. If you want to show this work, then you must manually copy into a markdown cell.
- Use feature branching with your username as prefix, e.g. *steve/oxygen* and create PRs against `dev`
- Once code has matured, as decided by consensus, it will move to `stable`

## Notes
- top level directory has a notebooks subdirectory for all Jupyter Notebooks _but_ then sym link the note books into the 'book' directory and the appropriate chapter