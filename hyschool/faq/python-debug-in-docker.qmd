---
title: "How to use the Python debugger inside docker"
date: 2022-07-05 
author: "Steve Harris"
---

# Question

How to I use the python debugger `pdb` inside a docker container?

# Answer

I got massively stuck trying to debug a python script in a running docker container.
On my own machine, I would have just used the [Python debugger](https://realpython.com/python-debugging-pdb/#stepping-through-code).
This [guide](https://blog.lucasferreira.org/howto/2017/06/03/running-pdb-with-docker-and-gunicorn.html) shows how to make that work from a running docker container.

