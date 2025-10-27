import glob
from setuptools import setup, Extension
from Cython.Build import cythonize

# Find all Python files to compile
py_files = glob.glob("**/*.py", recursive=True)
# Exclude main.py and setup.py
py_files = [f for f in py_files if f not in ["main.py", "setup.py"]]

extensions = [
    Extension(
        name.replace("/", ".").replace(".py", ""),
        [name],
        extra_compile_args=["-O3", "-march=native"],
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
    )
)
