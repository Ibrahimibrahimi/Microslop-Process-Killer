from cx_Freeze import setup, Executable
import os, time

# build binaries
setup(
    name="MyApp",
    version="2.0",
    description="Microslop Process Killer",
    executables=[Executable("killing_fck_microslop_useless_process.py")],
    options={
        "build_exe": {
            "packages": ["psutil"],
            "include_files": [
                ("settings.json", "settings.json"),
                ("settings.cfg", "settings.cfg"),
                ("tofuck.txt", "tofuck.txt"),
            ],
        }
    },
)

# create config files inside the build folder
time.sleep(2)
folder = "build/"
full_path = folder + os.listdir(folder)[0]

with open(f"{full_path}/settings.json", "w") as file:
    import json
    json.dump(
        {
            "process_names": [
                "TrustedInstaller.exe",
                "TiWorker.exe",
                "GoogleCrashHandler64.exe",
                "GoogleCrashHandler.exe",
            ],
            "process_list_file": "tokill.txt",
            "scan_interval": 3,
            "log_file": None,
            "dry_run": False,
            "verbose": False,
        },
        file,
        indent=4,
    )

with open(f"{full_path}/settings.cfg", "w") as file:
    file.write("true\n")
    file.write("tokill.txt")

with open(f"{full_path}/tokill.txt", "w") as file:
    for i in [
        "TrustedInstaller.exe",
        "TiWorker.exe",
        "GoogleCrashHandler64.exe",
        "GoogleCrashHandler.exe",
    ]:
        file.write(i + "\n")
