from distutils.core import setup
from Cython.Build import cythonize
import os

main_folder = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ui_folder = "UI"
py_folder = os.path.join(ui_folder, "py")
files = ["__init__.pyx", "converter.pyx", "main.pyx", "Vizualisation.pyx", os.path.join(ui_folder, "__init__.pyx"),
         os.path.join(py_folder, "__init__.pyx")]

files = tuple(os.path.join(main_folder, f) for f in files)
print(files)
setup(ext_modules=os.path.join(ui_folder, py_folder, "__init__.pyx"))
