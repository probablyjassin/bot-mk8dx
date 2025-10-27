from setuptools import setup, Extension
from Cython.Build import cythonize
import glob
import os

# Find all Python files to compile
py_files = glob.glob("**/*.py", recursive=True)
# Exclude main.py and setup.py
py_files = [f for f in py_files if f not in ["main.py", "setup.py"]]

# Ensure __init__.py exists in all package directories
for py_file in py_files:
    directory = os.path.dirname(py_file)
    if directory:
        os.makedirs(directory, exist_ok=True)

extensions = [
    Extension(
        name.replace("/", ".").replace(".py", ""),
        [name],
        extra_compile_args=["-O3", "-march=native", "-Wno-array-bounds"],
    )
    for name in py_files
]

setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            "language_level": "3",
            "embedsignature": True,
            "boundscheck": False,
            "wraparound": False,
        },
        build_dir="build",
    )
)
