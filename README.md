# volkanic

A simple command runner.


Create a YAML file, e.g. `print.yml`

    default:
        module: builtins
        call: print
        args:
        - Hello
        - Python
        kwargs:
            sep: "-"
            end: "~"

Run

    volk runconf print.yml
