# Contributing

## Setup

```bash
# Clone the repo
git clone https://github.com/austin-bowen/voicebox.git
cd voicebox

# Setup virtual env
python3 -m venv venv
. venv/bin/activate

# Install dependencies
pip install --editable .[all]
sudo apt install -y libportaudio2
python -m nltk.downloader punkt -d ./venv/nltk_data

# Run tests and generate coverage report
invoke test cov
```

## Running Tasks

Tasks like running tests, building and uploading artifacts to PyPI, etc.
are run using the `invoke <task>` command. Run `invoke -l` to list all
available tasks.
