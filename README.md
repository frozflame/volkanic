# volkanic

A simple command runner.


Create a YAML file, e.g. `print.yml`

```yaml
default:
    module: builtins
    call: print
    args:
    - Hello
    - Python
    kwargs:
        sep: "-"
        end: "~"
 ```


Run

```bash
volk runconf print.yml
```
