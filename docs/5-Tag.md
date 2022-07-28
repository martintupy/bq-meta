# Tag

For publishing distribution to Pypi we need to create tag fro github action

### 1. Git tag

```bash
git tag $TAG -a -m $MESSAGE
```

### 2. Push tag

```bash
git push origin --tags
```

## Summary

```bash
TAG=
MESSAGE=
git tag $TAG -a -m $MESSAGE
git push origin --tags
```
