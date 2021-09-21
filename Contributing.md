## Table of contents
* [Drawings](#1-dawings)
* [Write Code](#2-write-code)
* [Generate pip Package](#3-generate-pip-package)

## 1. Drawings
For drawings (e.g. in readme-files), we recomment to use the program [Inkscape](https://inkscape.org/). It is open source software and runs on Linux, Mac and Windows. If you want to draw electirc circuits, we recommend this library on [github](https://github.com/upb-lea/Inkscape_electric_Symbols).

## 2. Write Code

### 2.1 Sphinx documentation using docstrings
Documentation is generated by Sphinx, and Sphinx reads the docstrings inside the code. Make sure to keep the docstrings up-to-date when making a change!
Sphinx uses autodoc extension which generates documentation automatically by reading the docstrings.
The docstrings can be written in rst file format whereas other formats like google docstrings are also available.

Find a rst and sphinx cheat sheet [here](https://sphinx-tutorial.readthedocs.io/cheatsheet/)

Step 1: Use [sphinx-quickstart](https://www.sphinx-doc.org/en/master/man/sphinx-quickstart.html) feature of sphinx which will setup the required files.

Step 2: Configure the conf.py file with necessary extensions.

Step 3: Create the necessary .rst files like _introduction, installation, transistordatabase_ and add the tree structure in index.rst.

Step 4: Point to folder where Makefile exists and execute command _**"make html"**_ to generate documentation. The generated HTML files will be placed under _build\ folder.

For generating multiversion documentation, py module _sphinx-multiversion_ is used and added as extension in conf.py.
Further steps about configuring the project to enable multiversioning documentation can be found [here](https://holzhaus.github.io/sphinx-multiversion/master/quickstart.html).


### 2.2 Use type hints
Find a type hint cheat sheet [here](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)

## 3. generate pip package

### 3.1 generate requirements.txt
File 'requirements.txt' is auto generated by pipreqs. To install pipreqs, do the following
```
pip install pipreqs
```
Generate the 'requirements.txt'-file
```
pipreqs /home/project/location/transistor_database
```
Further information can be found [here](https://pypi.org/project/pipreqs/)

### 3.2 Generate pip-package by using setup.py
Some useful links
 * [classifiers](https://pypi.org/classifiers/)
Run setup.py as the following from your operating system command line
```
python3 setup.py bdist_wheel 
```
Please find the generated pip package inside the /dist-folder

### 3.3 Test the pip package from local installation before uploading 
```
python3 -m pip install transistordatabase-x.x.x-py3-none-any.whl  
```

### 3.4 Upload pip package to pypi
Run this from your operating system command line
```
twine upload --repository pypi dist/* 
```

### 3.5 Hint
Note: 2.2 and 2.3 can also be done by installing the package direct from the source code into python. You need to reinstall it after any change in the source-code if you want to work with the latest version.
```
cd /path/of/python/package
python3 -m pip install -e .
```

 