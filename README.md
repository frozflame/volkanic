volkanic
========

A simple command runner. To install

    python -m pip install volkanic

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
