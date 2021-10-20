SHELL := /bin/bash

# vars
PROJECT := messenger
LOCALPATH := ./
PYTHONPATH := $(LOCALPATH)/
DJANGO_SETTINGS_MODULE = $(PROJECT).settings
DJANGO_POSTFIX := --settings=$(DJANGO_SETTINGS_MODULE) --pythonpath=$(PYTHONPATH)
PYTHON_BIN := $(VIRTUAL_ENV)/bin

.PHONY: clean showenv collectstatic run build download tar install uninstall virtualenv browser all

showenv:
	@echo '======================================================================================'
	@echo 'FIRST TIME USAGE RUN (sudo make setup) or setup and run this commands (sudo make all)'
	@echo 'After the first time setup run (sudo make run) or (sudo make browser) to run on your default browser'
	@echo 'PROJECT Directory:' $(PROJECT)
	@echo 'DJANGO_SETTINGS_MODULE:' $(DJANGO_SETTINGS_MODULE)
	@echo '======================================================================================'


djangohelp: 
	python3 manage.py --help $(DJANGO_POSTFIX)

collectstatic: 
	-mkdir -p .$(LOCALPATH)/static
	python3 manage.py collectstatic -c --noinput $(DJANGO_POSTFIX)

run: 
	python3 manage.py runserver $(DJANGO_POSTFIX)

clean:
	find . -name "*.pyc" -print0 | xargs -0 rm -rf
	-rm -rf htmlcov
	-rm -rf .coverage
	-rm -rf build
	-rm -rf dist
	-rm -rf src/*.egg-info

browser: run
	python3 -c "import webbrowser; webbrowser.open('http://127.0.0.1:8000/')"

download:
	wget -c https://github.com/django/django/archive/refs/tags/3.2.8.tar.gz -P ./dependencies
	wget -c https://github.com/georgemarshall/django-cryptography/archive/refs/tags/1.0.tar.gz -P ./dependencies

tar:
	tar -xzf ./dependencies/3.2.8.tar.gz --directory=./dependencies
	tar -xzf ./dependencies/1.0.tar.gz --directory=./dependencies

install:  
	pip install -r ./requirements.txt
	#pip install ./dependencies/django-3.2.8
	#pip install ./dependencies/django-cryptography-1.0

uninstall:
	pip uninstall virtualenv -y
	pip uninstall Django -y
	pip uninstall django-cryptography -y

virtualenv:
	virtualenv . && source ./bin/activate
	
build: install virtualenv collectstatic browser 

all: build
