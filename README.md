# Microslop Process Killer
Kill useless microslop processes on Windows.

## Features
- Continuously monitors and terminates unwanted processes
- Configurable process list via JSON/YAML config files or plain text files
- Dry-run mode to preview what would be killed
- CLI argument parsing for easy automation
- Logging to file and/or stdout
- Signal handling for graceful shutdown
- Backward-compatible with legacy `settings.cfg`

## Usage

### Basic (runs with defaults)
```sh
python killing_fck_microslop_useless_process.py
```

### With config file
```sh
python killing_fck_microslop_useless_process.py -c settings.json
python killing_fck_microslop_useless_process.py -c settings.yaml
```

### Dry-run mode
```sh
python killing_fck_microslop_useless_process.py --dry-run
```

### List configured processes
```sh
python killing_fck_microslop_useless_process.py --list
```

### Single scan (no loop)
```sh
python killing_fck_microslop_useless_process.py --once
```

### Verbose logging
```sh
python killing_fck_microslop_useless_process.py --verbose --log-file process_killer.log
```

### Custom scan interval (seconds)
```sh
python killing_fck_microslop_useless_process.py --interval 10
```

## Configuration

### JSON format (`settings.json`)
```json
{
    "process_names": ["TrustedInstaller.exe", "TiWorker.exe"],
    "process_list_file": "tofuck.txt",
    "scan_interval": 3,
    "log_file": "process_killer.log",
    "dry_run": false,
    "verbose": false
}
```

### YAML format (`settings.yaml`)
```yaml
process_names:
  - TrustedInstaller.exe
  - TiWorker.exe
process_list_file: tofuck.txt
scan_interval: 3
log_file: null
dry_run: false
verbose: false
```

CLI arguments override config file values.

## How to build
### Install cx_Freeze exe builder module
```sh
pip install cx_Freeze
```

### Build the executable
```sh
python setup.py build
```
