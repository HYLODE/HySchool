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


