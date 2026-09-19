# This is a file which just gives you the commands for setting up a python venv for this project

- For deleting the old environment (if messed up)

```
deactivate 2>/dev/null
rm -rf venv
```

- For creating a new one

```
python3 -m venv venv
source venv/bin/activate
```

- for installing dependencies

```
pip install --upgrade pip
pip install torch pytesseract torchvision transformers pillow accelerate
```
