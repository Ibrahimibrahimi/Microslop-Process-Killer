# Microslop-Process-Killer
Kill useless microslop process

# How to build
### install cx_Freeze exe builder module
```sh
pip install cx_Freeze
```

### create the setup file
```python
# let's say you want to build  myfile.py
from cx_Freeze import setup, Executable

setup(
    name="MyApp",
    version="1.0",
    description="My Python App",
    executables=[Executable("myfile.py")]
)
```

### locate the target file
├── myfile.py # file to build
├── tofuck.txt # list of useless process
├── settings.cfg # settings (line1 = either to load settings.cfg or not , line2 = path to tofuck.txt)
└── setup.py # builder script

### build
```sh
python setup.py buid
```
