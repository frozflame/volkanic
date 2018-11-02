# volkanic

A simple command runner.


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
