




## Run the example

### Requirements

You need:
- Python 3.10.12 or higher.
- A [OpenAI API key](https://platform.openai.com/account/api-keys).
- [pipenv](https://pipenv.pypa.io/en/latest/) (`pip install --user pipenv`)

### Prepare the environment

- Create a virtual environment: `python -m venv .venv`
- Activate the virtual environment:
    * linux: `source .venv/bin/activate`
    * windows: `.venv\Scripts\activate.bat`
- Install the dependencies: `pip install -e .`.
- Verify that everything is working fine: `python -m unittest discover tests/`

> *Note*:
> - Create the file "requirements.txt": `pip freeze > requirements.txt`





