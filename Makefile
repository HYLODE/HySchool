# Makefile for analysis report

.PHONY: preview jupyter

jupyter:
	jupyter lab

preview:
	quarto preview hyschool

