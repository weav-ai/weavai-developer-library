## Setup 

### Create a new virtual environment

```
python3 -m venv myenv
```

### Activate the virtual environment

```
source myenv/bin/activate
```

### Change directory into `package` folder
```
cd package
```

### There are 2 ways to install the package.
### Option 1: Direct install using `pip`
```
pip3 install .
```

### Option 2: Building the wheel distribution
### Run 
```
pip3 install -q build
```

```
python3 -m build
```

### You will now observe a `dist/` folder generated in the `package` directory containing a `.tar.gz` file and a `.whl` file.
### Run `pip` install on the `.whl` file
```
pip3 install build dist/weavaidev-0.0.1-py3-none-any.whl
```



## The library is now installed in the virtual environment.
### Play around with some sample examples are provided in `examples` folder. 
### Place your `.env` file in the same directory as where you would use it, in this case, the `examples` folder.