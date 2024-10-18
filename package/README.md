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

### Build the wheel for the package
```
python3 -m build
```

### You will observe `dist` folder created in the same directory.
### Install the package using

```
pip3 install dist/weavaidev-0.0.1-py3-none-any.whl
```

### The library is now installed in the virtual environment.
### Play around with some sample examples are provided in `examples` folder. 
### Place your `.env` file in the same directory as where you would use it, in this case, the `examples` folder.