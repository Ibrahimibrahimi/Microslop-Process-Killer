import psutil
import time
import os

# Configuration
config_file = "settings.cfg"
FROM_FILE = False
PATH = "empty"

# Load configuration from file
if os.path.exists(config_file):
    print("Found config file, loading...")
    with open(config_file, "r") as file:
        content = [line.strip() for line in file.readlines()]
        # Parse the first line for boolean
        FROM_FILE = content[0].lower() == "true" if len(content) > 0 else False
        # Parse optional second line for path
        if len(content) > 1:
            PATH = content[1]
else:
    print("No config file found. Proceeding with defaults.")

# Default list of processes to kill
tokill = ["TrustedInstaller.exe", "TiWorker.exe","GoogleCrashHandler64.exe","GoogleCrashHandler.exe"]

# Ask user if they want to load additional processes from a text file
if os.path.exists(PATH):
    with open(PATH, "r") as file:
        content = [line.strip() for line in file.readlines()]
        print(f"Loaded {len(content)} items!")
        tokill.extend(content)
else:
    print("Path not found. Continuing with default process list.")

def get_running_processes():
    """Return a list of tuples (name, pid) for all running processes."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            info = proc.info
            processes.append((info['name'], info['pid']))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def kill_process(pid):
    """Attempt to kill process by pid."""
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

def main():
    while True:
        processes = get_running_processes()
        # Create a set of process names for faster lookup
        process_names = {name for name, _ in processes}
        for name, pid in processes:
            # if in black list
            if name in tokill:
                print(f"Found '{name}' (PID: {pid})! Attempting to kill...")
                kill_process(pid)

        # Sleep for a while before next check
        time.sleep(3)

if __name__ == "__main__":
    main()
