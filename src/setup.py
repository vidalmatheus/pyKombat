import sys
from cx_Freeze import setup, Executable
import pygame

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
        Executable("pykombat.py", base=base)
]

buildOptions = dict(
        packages = [],
        includes = [],
        include_files = [],
        excludes = []
)




setup(
    name = "pyKombat",
    version = "1.0",
    description = "pyKombat",
    options = dict(build_exe = buildOptions),
    executables = executables
 )
