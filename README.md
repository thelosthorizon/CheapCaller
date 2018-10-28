# CheapCaller

Find the cheapest operator to call with for a given phone numer.

## Dependencies

* python2.7
* python-pip
* virtualenv

## Things to keep in mind

> Not designed with portability in mind. Should work in all _debian based linux distros_.

> Any mention of __*make*__ here is a reference to __*GNU make*__.

> An operator file is a _plain text file_ with __.operator__ extension containing __comma separated extension and price__.

> __Name of the operator file is crucial__ and it should be __{*operator_name*}.operator__, this is how __CheapCaller knows of the operator name__.

> You are expected to be at top level of __CheapCaller repo__ at all times for it to work.

> `cheap_caller.py`: The positional arguments are the __phone number of interest__ and __directory__ where to recursively look for operator files.

> `cheap_caller.py`: __Cheapest operator and price__ will be printed in console if found.

> `cheap_caller.py`:  Default log level is info (Whats printed out on your console).

> `generate_operator_data.py`: The positional argument is __operator name__.

## Steps

1. Get the code
Clone the CheapCaller repository: https://github.com/thelosthorizon/CheapCaller.git

2. Install dependencies

If you are on _debian based linux distros_ and you do not have the dependencies, build the make target `make prepare-dev` _the first time_.

For other platforms, you can install the dependencies above using suitable means for the platform of interest.

3. Prepare data

You can generate operator data txt files with .operator extension that the CheapCaller consumes by running:

    $ make generate-operator-data name=telia number=5000
    $ make generate-operator-data name=telia

Or executing `generate_operator_data.py` script like:

    $ python generate_operator_data.py telia -n 3000
    $ python generate_operator_data.py telia

Either way, you will have a file called {name}.operator in data folder that can be ingested by CheapCaller application.

4. Run the application

Build _make targets_ of interest. Simply run `make` to get help. If you do not have `make` then execute `cheap_caller_py` and `generate_operator_data.py` scripts directly.
(Instructions below in __Usage__)

## Usage in detail

1. Make targets

Build make target `make run` like:

    $ make run phonenumber=123456 operatordir=./data pattern='"*.operator"' loglevel=debug
    $ make run phonenumber=123456 operatordir=./data

> pattern='"*.operator"', note the quotes they are on purpose. We want "*.operator" by `make` to
`cheap_caller.py`

> `make run` just calls `cheap_caller.py` forwarding the arguments passed in command line.

2. Executing scripts directly

Execute the `cheap_caller.py` script like:

    $ python cheap_caller.py 123456 ./data -ll debug -p '*.operator'
    $ python cheap_caller.py 123456 ./data

> -p '*.operator', note the quotes they are on purpose. we want pattern to pe passed undiluted,
no shell expansion.

> If executing `cheap_caller.py` or `generate_operator_data.py`scripts directly, you have to activate virtualenv by running: `. venv/bin/activate` and deactivate when done by simply typing `deactive` (__Note: activating and deactivating virtualenv is platform dependent, check virtualenv docs for more info__). It is assumed that all the dependencies have been installed.

## Options

### options that `make run` takes:

option | description | possible values
-------|----------   | ---------------
 phonenumber     | Phone number of interest. | MANDATORY
 operatordir     | Directory where to look for operator files. | MANDATORY
 pattern         | Pattern to use when looking for operator files. | OPTIONAL (default=*.operator)
 loglevel        | Desired logging leval. | OPTIONAL (default=info) POSSIBLE VALUES debug, info,                      error, warning, critical.

### options that `make generate-operator-data` takes

option | description | possible values
-------|----------   | ---------------
 name     | Operator name. | MANDATORY
 number   | Number of entries. | OPTIONAL (default=1000)

### optional arguments that `cheap_caller.py` script takes (executing cheap_caller.py script directly)

option | description | possible values
-------|----------   | ---------------
 -p    | pattern to use when looking for operator files. | OPTIONAL (default=*.operator)
 -ll   | Desired logging leval. | OPTIONAL (default=info) POSSIBLE VALUES debug, info,                      error, warning, critical.

### optional arguments that `generate_operator_data.py` script takes (executing generate_operator_data.py script directly)

option | description | possible values
-------|----------   | ---------------
 -n    | Desired number of entries. | OPTIONAL(default=1000)


## Running tests

Run the tests(_with coverage report_) simply building make target `make test`

## Linting

Check the code for errors and style conventions(_PEP-8_) `make lint`

## Cleanup

Delete the venv folder and also coverage execution data building make target `make clean`

## Directory structure:

Here you can see the directory structure of the CheapCaller.
```
├── cheap_caller
│   ├── parser.py
│   ├── helpers.py
│   ├── [....]
├── data
│   ├── [some operator files(*.operator)]
├── tests
│   ├── test_helper.py
│   ├── test_parser.py
│   ├── [....]
│   ├── data
│   │   ├── test_data1.operator
│   │   ├── [....]
├── cheap_caller.py
├── generate_operator_data.py
├── Makefile
├── README.md
├── requirements.txt
├── .pylintrc
```

#### cheap_caller folder
Contains all the necessary modules.

#### tests folder
All the unitests are here.

#### data folder
Some sample operator files to play with.