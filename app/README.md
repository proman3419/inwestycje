## Setup guide

### Prerequisites
- pyenv >=2.3.36
- poetry >=1.7.1

### Setup
Install the required python version
```bash
pyenv install 3.11.7
```
Create a virtual environment and install dependencies
```bash
poetry install
```

### Run
Enter the virtual environment shell
```bash
poetry run bash
```
Now you can run the application
```bash
python main.py
```
Alternatively, you can run the application directly from your shell
```bash
poetry run python main.py
```