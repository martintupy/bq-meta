# Package - test

https://packaging.python.org/en/latest/tutorials/packaging-projects/

## 1. Install python twine module

```bash
python3 -m pip install --upgrade twine
```

## 2. Check

```bash
twine check dist/*
```

## 3. Test upload

```bash
twine upload --repository testpypi dist/*
```

## 4. Test install

```bash
python -m pip install --index-url https://test.pypi.org/simple/ bq-meta
```

## 5. Upload

```bash
twine upload dist/*
```
