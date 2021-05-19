find ./dist/ -mindepth 2 -delete
python -m build
python -m twine upload --repository testpypi dist/*
