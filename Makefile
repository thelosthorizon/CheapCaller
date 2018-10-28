.PHONY: help prepare-dev lint test clean run generate-operator-data
# relative path to cur folder
# notdir extracts all but directory part of pwd
CURRENTDIR=$(notdir $(shell pwd))
VENV_NAME?=venv
# activate script
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
PYTHON=${VENV_NAME}/bin/python2
loglevel?=info
number?=1000
pattern?="*.operator"

.DEFAULT: help

help:
	@echo "make prepare-dev"
	@echo "       prepare development environment, use only once"
	@echo "make run phonenumber=<phoneno> operatordir=<directory> pattern=<pattern> loglevel=<level>"
	@echo "       run cheap_caller application"
	@echo "make generate-operator-data name=<name> number=<number>"
	@echo "       generate operator data"
	@echo "make test"
	@echo "       run tests"
	@echo "make lint"
	@echo "       run pylint"
	@echo "make clean"
	@echo "       cleanup"

prepare-dev:
	sudo apt-get -y install python2.7 python-pip
	python2 -m pip install virtualenv

# Will call $(VENV_NAME)/bin/activate target if it is newer than
# the venv file, or $(VENV_NAME)/bin/activate doesn’t exist.
# It will call the $(VENV_NAME)/bin/activate rule first.
venv: $(VENV_NAME)/bin/activate

$(VENV_NAME)/bin/activate: requirements.txt
# if requirement does change i.e. it is newer than $(VENV_NAME)/bin/activate
# update  the virtualenv
	test -d $(VENV_NAME) || virtualenv -p python2 $(VENV_NAME)
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install -r requirements.txt
# update the modification time of $(VENV_NAME)/bin/activate
# so next time it is not considered old
	touch $(VENV_NAME)/bin/activate

lint: venv
	${PYTHON} -m pylint cheap_caller --rcfile=.pylintrc
# lint recipe will fail if score is not 10
# We can just add  || true  after the command above
# but striving for perfect score

run: venv
	${PYTHON} cheap_caller.py ${phonenumber} ${operatordir} -p ${pattern} -ll ${loglevel}

generate-operator-data: venv
	${PYTHON} generate_operator_data.py ${name} -n ${number}

test: venv
	${VENV_ACTIVATE}; \
	python -c "import sys;print sys.executable"; \
	coverage run -m --source cheap_caller unittest discover --verbose; \
	coverage report -m; \
	deactivate;

clean:
# - in front to ignore exit status of command run
# deletes the virtualenv dir venv
	-rm -rf $(VENV_NAME)
	-rm -f .coverage