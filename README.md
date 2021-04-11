# AlignmentReporter

A tool for DM to easily make __Alignment Change Graphs__ for their Campaigns, __with a save system__
to switch between parties. Originally just a part of a larger toolbox, I am currently making it a standalone project. 
It is a bit old and need some changes (mainly using coroutines and C compilation).

The tool is quite simple in its way but I will add a tutorial later. For testing, simply launche the __init__.py at the 
root directory and enter a save file name. It will automatically load any existing file in the data folder if it exists. 
I have **already created two save files from personnal games** (accessible with the names "**Celtaidd**" and "**Volac**").

The generated images are in the "***AlignmentReporter/out/***" directory but a preview is loaded in the tool

*Python version*: **3.8.5**

## Installation:
in the root directory
```
python setup.py install
```

## Typical usages: 

### Python:  
```python
import AlignmentReporter as AR; AR.launch()
```

### in terminal: 

```
AlignR-Launch
```
