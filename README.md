Commands:

```console
$ python -m ironbot events  # list all Ironman professional races details
$ python -m ironbot list-events  # list codes for Ironman events (to be used with the next command)
$ python -m ironbot start-list <NUMBER>  # get the URL to download the PDF with the start list
```

Depends on `pdftotext` which [requires `poppler` to be installed](https://github.com/jalan/pdftotext#os-dependencies).
