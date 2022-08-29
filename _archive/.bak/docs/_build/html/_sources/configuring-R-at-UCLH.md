# Configuring R at UCLH

Tips and tricks if this is your first time working with R on the Datascience Desktop.


## A .Renviron file

You will need to create a `.Renviron` file in your home directory.

An example file is available [here](TODO: add gist). Within the file, you will need the following

### Proxies for connecting to the internet

This is not needed for packages installed from CRAN but it is needed for github installs etc.

```sh
http_proxy=http://www-cache-n.xuclh.nhs.uk:3128/
https_proxy=http://www-cache-n.xuclh.nhs.uk:3128/
HTTP_PROXY=http://www-cache-n.xuclh.nhs.uk:3128/
HTTPS_PROXY=http://www-cache-n.xuclh.nhs.uk:3128/
```
