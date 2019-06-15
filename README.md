volkanic
========

A simple command runner. To install (add `sudo` if necessary)

    python3 -m pip install volkanic


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

Say you have a package named `newpkg`


    newpkg
    ├── MANIFEST.in
    ├── docs
    ├── newpkg
    │   ├── __init__.py
    │   ├── algors.py
    │   ├── formatters.py
    │   ├── main.py
    │   └── parsers.py
    ├── requirements.txt
    ├── setup.py
    └── test_newpkg


In one of your functional modules, e.g. `newpkg/newpkg/formatter.py`,
provide a entry function which takes exactly 2 arguments:


```
def format_text(path):
    # actual code here
    return


def run(prog=None, args=None):
    desc = 'human readable formatter'
    parser = argparse.ArgumentParser(prog=prog, description=desc)
    parser.add_argument('-i', '--input-file', help='path to your input file')
    ns = parser.parse_args(args)
    format_text(ns.input_file)
```


Sub-command registry in `newpkg/newpkg/main.py`:


```python
import volkanic

entries = {
    # shorthand for "newpkg.formatter:run": "fmt",
    "newpkg.formatter": "fmt",
    "newpkg.parsers:run_yml_parser": "yml",
    "newpkg.parsers:run_ini_parser": "ini",
    # ...
}
registry = volkanic.CommandRegistry(entries)
```



Configure top-command in `newpkg/setup.py`:

```python
setup(
    name="Flask",
    ...
    entry_points={"console_scripts": ["newcmd = newpkg.main:registry"]},
)
```


Install package `newpkg` or link with `python3 setup.py develop`.

Now you have command `newcmd`:

    $ newcmd
    availabe commands:
    - fmt
    - ini
    - yml
    ...

Run with sub-command `fmt`:

    $ newcmd fmt -h

-------------------------------------------------------------------------
### Run YAML

Create a YAML file, e.g. `print.yml`

```yaml
default:
    module: builtins
    call: print
    args:
    - volkanic
    - command
    kwargs:
        sep: "-"
        end: "~"
 ```

Run

```bash
$ volk runconf print.yml
volkanic-command~
```
