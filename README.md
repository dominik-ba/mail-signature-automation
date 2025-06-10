# repo / app name

xyz

## usage

locally on your windows machine do this

```bash
pipenv install
pipenv shell
python3 main.py "<name of your signatue file>"
```

In the devcontainer do this
```bash
pipenv run python3 main.py "<name of your signatue file>" -p /workspace/signatures/
```

e.g.
```bash
pipenv run python3 main.py "default (dominik.bartsch@capgemini.com)" -p /workspace/signatures/
pipenv run python3 main.py "response (dominik.bartsch@capgemini.com)" -p /workspace/signatures/
```

## other things
