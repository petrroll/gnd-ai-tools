# Based on: https://blog.horejsek.com/makefile-with-python/
VENV_NAME?=env
PYTHON=$(VENV_NAME)/bin/python
PYTHON_GLOBAL=python3


prereq: $(VENV_NAME) prereq-apt 

prereq-apt:
	# pyaudio (speech to text)
	apt-get install portaudio19-dev	
	# tts engine
	apt-get install espeak
	touch prereq-apt

# ENV
$(VENV_NAME): requirements.txt
	@test -d $(VENV_NAME) || $(PYTHON_GLOBAL) -m venv $(VENV_NAME)
	$(PYTHON) -m pip install -r requirements.txt

clean_$(VENV_NAME): 
	rm -rf $(VENV_NAME)

# Common:
clean_pycache:
	rm -rf __pycache__

clean: clean_$(VENV_NAME)  clean_pycache 
	rm -rf prereq-apt


