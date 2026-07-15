import psutil
import time


tokill = ["TrustedInstaller.exe","TiWorker.exe"]

# attempt to load from text file
from_text = input("Use a text list file ? (empty=No)")

if from_text.strip() != "" :
    path = input("Path for list of process to kill : ")
    import os
    if os.path.exists(path) :
        # load to 'tokill' array
        with open(path,"r") as file :
            content = [i.strip() for i in file.readlines()]
            print("Loaded",len(contenet)," Items !")
            tokill += content
    else :
        print("Path not found")

def get_running_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            process_info = proc.info
            processes.append((process_info['name'], process_info['pid']))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes


def kill(pid):
    try:
        proc = psutil.Process(pid)
        proc.kill()
        print(f"Process with PID {pid} has been terminated.")
    except psutil.NoSuchProcess:
        print(f"No process found with PID {pid}.")
    except psutil.AccessDenied:
        print(f"Permission denied to terminate process with PID {pid}.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage:

while True :
    for name, pid in get_running_processes():
        if name in tokill :
            print(f"Found {name} at {pid} !")
            kill(pid)
        else :
            print(f"Not found")
            time.sleep(4)
    time.sleep(3)
