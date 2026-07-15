from cx_Freeze import setup, Executable
import os,time


# build binaries
setup(
    name="MyApp",
    version="1.0",
    description="My Python App",
    executables=[Executable("killing_fck_microslop_useless_process.py")]
)

# create config files inside the folder

time.sleep(2) # wait until build is complete
folder = "build/"
full_path = folder + os.listdir(folder)[0] # get build folder

with open(f"{full_path}/settings.cfg","w") as file :
    file.write("true\n")
    file.write("tofuck.txt")

with open(f"{full_path}/tofuck.txt","w") as file :
    for i in ["TrustedInstaller.exe", "TiWorker.exe","GoogleCrashHandler64.exe","GoogleCrashHandler.exe"] :
        file.write(i + "\n")
