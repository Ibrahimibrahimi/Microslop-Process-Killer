#!/usr/bin/env python3
"""Microslop Process Killer - Kill useless Windows processes.

Continuously monitors and terminates unwanted processes.
Supports YAML/JSON config files, dry-run mode, CLI arguments,
and process kill logging.
"""

import argparse
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

try:
    import psutil
except ImportError:
    print("Error: psutil is required. Install with: pip install psutil", file=sys.stderr)
    sys.exit(1)

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

DEFAULT_CONFIG = "settings.json"
DEFAULT_LOG_FILE = "process_killer.log"

DEFAULT_PROCESS_LIST = [
    "TrustedInstaller.exe",
    "TiWorker.exe",
    "GoogleCrashHandler64.exe",
    "GoogleCrashHandler.exe",
]

logger = logging.getLogger("process_killer")

_shutdown_requested = False


def handle_signal(signum, frame):
    global _shutdown_requested
    _shutdown_requested = True
    logger.info("Shutdown signal received, stopping after current cycle...")


def setup_logging(log_file=None, verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )


def load_config(config_path):
    """Load configuration from JSON or YAML file.

    Config format:
    {
        "process_names": ["TrustedInstaller.exe", ...],
        "process_list_file": "tofuck.txt",
        "scan_interval": 3,
        "log_file": "process_killer.log",
        "dry_run": false,
        "verbose": false
    }
    """
    path = Path(config_path)
    if not path.exists():
        logger.warning("Config file '%s' not found, using defaults.", config_path)
        return {}

    with open(path, "r", encoding="utf-8") as f:
        if path.suffix in (".yaml", ".yml"):
            if not HAS_YAML:
                logger.error("PyYAML is required for YAML config. Install with: pip install pyyaml")
                sys.exit(1)
            return yaml.safe_load(f) or {}
        elif path.suffix == ".json":
            return json.load(f)
        elif path.suffix == ".cfg":
            return _load_cfg(path)
        else:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.error("Cannot parse config file '%s'. Use JSON or YAML.", config_path)
                return {}


def _load_cfg(path):
    """Legacy settings.cfg parser for backward compatibility."""
    with open(path, "r", encoding="utf-8") as f:
        content = [line.strip() for line in f.readlines()]
    cfg = {}
    if len(content) > 0:
        cfg["process_list_from_file"] = content[0].lower() == "true"
    if len(content) > 1:
        cfg["process_list_file"] = content[1]
    return cfg


def load_process_names(config):
    """Build the final list of process names to kill from config + legacy sources."""
    names = list(DEFAULT_PROCESS_LIST)

    if "process_names" in config:
        names.extend(config["process_names"])

    legacy_file = config.get("process_list_file", "tofuck.txt")
    load_from_file = config.get("process_list_from_file", True)

    if load_from_file:
        file_path = Path(legacy_file)
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                extra = [line.strip() for line in f if line.strip()]
            logger.info("Loaded %d additional process names from '%s'", len(extra), legacy_file)
            names.extend(extra)
        else:
            logger.warning("Process list file '%s' not found.", legacy_file)

    deduped = list(dict.fromkeys(names))
    logger.info("Watching %d unique process names.", len(deduped))
    return deduped


def get_running_processes():
    """Return a list of (name, pid, cpu_percent) for all running processes."""
    processes = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            info = proc.info
            processes.append((info["name"], info["pid"], proc))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes


def kill_process(proc_obj, dry_run=False):
    """Attempt to kill a process. Returns True if killed, False otherwise."""
    try:
        name = proc_obj.name()
        pid = proc_obj.pid
        if dry_run:
            logger.info("[DRY RUN] Would kill '%s' (PID %d)", name, pid)
            return True
        proc_obj.kill()
        logger.info("Killed '%s' (PID %d)", name, pid)
        return True
    except psutil.NoSuchProcess:
        logger.debug("Process PID %d already gone.", getattr(proc_obj, "pid", "?"))
    except psutil.AccessDenied:
        logger.warning("Access denied killing PID %d.", getattr(proc_obj, "pid", "?"))
    except Exception as e:
        logger.error("Error killing process: %s", e)
    return False


def scan_and_kill(process_names, dry_run=False):
    """Scan for target processes and kill them. Returns count of killed."""
    running = get_running_processes()
    killed = 0
    for name, pid, proc_obj in running:
        if name in process_names:
            if kill_process(proc_obj, dry_run=dry_run):
                killed += 1
    return killed


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Microslop Process Killer - Terminate useless Windows processes."
    )
    parser.add_argument(
        "-c", "--config",
        default=DEFAULT_CONFIG,
        help="Path to JSON/YAML config file (default: %(default)s)",
    )
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        default=None,
        help="Show what would be killed without actually killing",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=None,
        help="Enable debug logging",
    )
    parser.add_argument(
        "-i", "--interval",
        type=float,
        default=None,
        help="Scan interval in seconds (default: 3)",
    )
    parser.add_argument(
        "-l", "--log-file",
        default=None,
        help="Path to log file (default: none, stdout only)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        default=False,
        help="Run a single scan and exit instead of looping",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        default=False,
        help="List configured process names and exit",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    config = load_config(args.config)

    cli_overrides = {}
    if args.dry_run is not None:
        cli_overrides["dry_run"] = args.dry_run
    if args.verbose is not None:
        cli_overrides["verbose"] = args.verbose
    if args.interval is not None:
        cli_overrides["scan_interval"] = args.interval
    if args.log_file is not None:
        cli_overrides["log_file"] = args.log_file

    config.update({k: v for k, v in cli_overrides.items() if v is not None})
    # For booleans that are explicitly set via CLI, always take them
    if args.dry_run is not None:
        config["dry_run"] = args.dry_run
    if args.verbose is not None:
        config["verbose"] = args.verbose

    dry_run = config.get("dry_run", False)
    verbose = config.get("verbose", False)
    interval = config.get("scan_interval", 3)
    log_file = config.get("log_file", None)

    setup_logging(log_file=log_file, verbose=verbose)

    if dry_run:
        logger.info("=== DRY RUN MODE - No processes will be killed ===")

    process_names = load_process_names(config)

    if args.list:
        print("Configured target processes:")
        for name in process_names:
            print(f"  - {name}")
        return 0

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    logger.info("Starting process killer (interval=%.1fs, dry_run=%s)", interval, dry_run)

    total_killed = 0
    scan_count = 0

    while not _shutdown_requested:
        try:
            killed = scan_and_kill(process_names, dry_run=dry_run)
            total_killed += killed
            scan_count += 1
            if killed > 0:
                logger.info("Scan #%d: killed %d process(es) (total: %d)", scan_count, killed, total_killed)
            else:
                logger.debug("Scan #%d: no target processes found.", scan_count)
        except Exception as e:
            logger.error("Error during scan: %s", e)

        if args.once:
            break

        time.sleep(interval)

    logger.info("Stopped. Ran %d scan(s), killed %d process(es).", scan_count, total_killed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
