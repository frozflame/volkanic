volkanic
========

Auxiliary tools dealing with paths and config files. 

To install (add `sudo` if necessary)

    python3 -m pip install volkanic


### GlobalInterface and config file

Example:

`GlobalInterface` is defined in `example/environ.py` as:

```python
import volkanic


class GlobalInterface(volkanic.GlobalInterface):
    # you should always define `package_name`
    package_name = 'example'
```

Configuration file `config.json5`:

```json5
{
    "upstram_prefix": "http://127.0.0.1:9100",
    "sqlite": "/data/local/example/db.sqlite"
}
```

This `config.json5` is at one of the follow locations:
- Under your project directory in a development enviornment
- `~/.example/config.json5`
- `/etc/example/config.json5`
- `/example/config.json5`

Access config:

```
>>> from example.environ import GlobalInterface 
>>> gi = GlobalInterface()  # note that GlobalInterface is a singlon class
>>> print(gi.conf)
{'data_dir': '/data/local/example', 'sqlite': '/data/local/example/db.sqlite'}
```

Note that `GlobalInterface` is a singlon class, which means that 
`GlobalInterface()` will always return the same object:
```
>>> GlobalInterface() is GlobalInterface()
True
```

The recommended usage of `GlobalInterface()` is to create instanciate it 
at the top each module:

```python
import re
import math
from example.tools import your_funny_tool  # noqa

gi = GlobalInterface()


def find_funny_things():
    url = gi.conf['upstram_prefix'] + '/funny-api'
    path = gi.under_package_dir('asset/funny.json')
    # more code here ...
```


-------------------------------------------------------------------------
### Accessories

List sub-commands

    $ volk
    availabe commands:
    - a
    - o
    - runconf
    - where

Locate a Python package directory with `volk where`:

    $ volk where requests
    requests	/usr/local/lib/python3.6/site-packages/requests


You can open a file or URL with default application with `volk o`.

To open current directory with default file manager (Finder / explorer.exe / ...)

    $ volk o .

Show `sys.argv`:

    $ volk a \; "hello world" hello python
    0	'/usr/local/bin/volk'
    1	'a'
    2	';'
    3	'hello world'
    4	'hello'
    5	'python'

-------------------------------------------------------------------------
### Sub-command protocal

Say you have a package named `mypkg`


    mypkg/
    ├── MANIFEST.in
    ├── docs/
    ├── mypkg/
    │    ├── __init__.py
    │    ├── algors.py
    │    ├── formatters.py
    │    ├── main.py
    │    └── parsers.py
    ├── requirements.txt
    ├── setup.py
    └── tests/


In one of your functional modules, e.g. `mypkg/mypkg/formatter.py`,
provide a entry function which takes exactly 2 arguments:


```python
import argparse

def process_file(path):
    # actual code here
    return

def run(prog=None, args=None):
    desc = 'human readable formatter'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    add = parser.add_argument
    add('-i', '--input-file', help='path to your input file')
    ns = parser.parse_args(args)
    process_file(ns.input_file)
```


Sub-command registry in `mypkg/mypkg/main.py`:


```python
import volkanic

commands = {
    "fmt": "mypkg.formatter",
    "yml": "mypkg.parsers:run_yml_parser",
    "ini": "mypkg.parsers:run_ini_parser",
}
registry = volkanic.CommandRegistry(commands)
```

Note that `mypkg.formatter` is a shorthand for `mypkg.formatter:run`.


Configure top level command in `mypkg/setup.py`:

```python
from setuptools import setup

setup(
    name="mypkg",
    entry_points={"console_scripts": ["mycmd = mypkg.main:registry"]},
    # more arguments here
)
```


Install package `mypkg` or link with `python3 setup.py develop`.

Now you have command `mycmd`:

    $ mycmd
    availabe commands:
    - fmt
    - ini
    - yml

Run with sub-command `fmt`:

    $ mycmd fmt -h

