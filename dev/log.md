2022-09-03
install quarto extension for videos
https://github.com/quarto-ext/video


2022-09-01
using the default hyschool environment now
b/c I think it's largely the same
https://docs.jupyter.org/en/latest/
https://jupyterlab.readthedocs.io/en/stable/
set up a local config by runnning

```sh
jupyter lab --generate-config
```


2022-08-29
clean branch quarto
moved all files including hidden into `./_archive`
working with default quarto environment

```sh
cd hyschool
conda create --name quarto python=3.9 jupyter matplotlib plotly_express
conda activate quarto
```

then followed instructions here
https://quarto.org/docs/websites/

```sh
quarto create-project hyschool --type website
quarto preview hyschool
```


