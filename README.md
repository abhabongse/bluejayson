# BlueJayson

BlueJayson revives itself as a collection of extra annotation utilities
into type annotations in functions, classes, and modules. 
It is intended to be used with `typing.Annotated` ([PEP 593](https://www.python.org/dev/peps/pep-0593/))
which is available since `python3.9` (also backported by [`typing-extensions`](https://pypi.org/project/typing-extensions/) package).


## Why Another Library?

Other libraries doing similar tasks do not fit my use case and my taste.
So I write another one so that I can use in my own production code.
It is also my opportunity to practice meta-programming in Python.


## Important Note

-   This project is still in active development stage.
    Minor upgrades may break backward-compatibility.
-   For bug reports or suggestions,
    please use [issues page](https://github.com/abhabongse/bluejayson/issues) on GitHub.
    Other questions about the project itself (e.g. if you are seeking help with the usage)
    may be asked on [discussions page](https://github.com/abhabongse/bluejayson/discussions).
    

## Developing Note

`Makefile` contains a lot of utility scripts.  
See help command by simply running `make` or `make help`.
