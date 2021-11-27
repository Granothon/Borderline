from cx_Freeze import setup, Executable

base = None    

executables = [Executable("main.py", base=base)]

packages = ["idna", "pygame", "random", "math"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "Borderline",
    options = options,
    version = "1.5",
    description = 'Space themed Shoot-em-Up. My second game',
    executables = executables
)