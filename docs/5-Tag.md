# Tag

For publishing distribution to Pypi we need to create tag fro github action

## 1. Git tag

```bash
git tag <tagname> -a -m <message>
```

e.g.

```bash
git tag 0.5.0 -a -m "Make fullscreen CLI"
```

## 2. Push tag

```bash
git push origin --tags
```