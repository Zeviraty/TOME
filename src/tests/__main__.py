# Importing and running tests
import os
from importlib import util as importutil
import time
import threading
import time

def load_namespaces(test_dir: str ="tests"):
    spaces = []
    for filename in os.listdir(test_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            path = os.path.join(test_dir, filename)
            name = filename[:-3]
            spec = importutil.spec_from_file_location(name, path)
            if spec is None:
                continue
            if spec.loader is None:
                continue
            module = importutil.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module,"TESTS"):
                spaces.append({'name': name if not hasattr(module,"NAME") else module.NAME,
                              'tests': module.TESTS})
    return spaces

def rpad(s: str): return s.ljust(os.get_terminal_size()[0], ".")

def format_duration(seconds: float) -> str:
    units = [
        (1e-9, "ns"),
        (1e-6, "µs"),
        (1e-3, "ms"),
        (1.0,  "s"),
    ]

    for threshold, suffix in units:
        if seconds < threshold * 1000 or suffix == "s":
            value = seconds / threshold
            return f"{value:.2f}{suffix}"
    return "0s"

def progress_printer(start_time, stop_event):
    while not stop_event.wait(0.1):
        elapsed = time.perf_counter() - start_time
        print(
            "\33[2K\r" +
            rpad(f"Running [{format_duration(elapsed):>10}] "),
            end='',
            flush=True
        )

def main():
    spaces = load_namespaces()
    os.chdir("..")
    failed = 0
    all_start = time.perf_counter()

    for namespace in spaces:
        for test in namespace['tests']:

            stop_event = threading.Event()
            printer = threading.Thread(
                target=progress_printer,
                args=(all_start, stop_event),
                daemon=True
            )
            printer.start()

            start = time.perf_counter()

            test_class = test()
            status = test_class.run()

            stop_event.set()
            printer.join()

            elapsed = time.perf_counter() - start

            print("\33[2K\r", end='', flush=True)
            if status:
                print(
                    f"\x1b[1;32mPASS\x1b[0m "
                    f"[{format_duration(elapsed):>10}] "
                    f"\x1b[0;35m{namespace['name']}::{test_class.name}\x1b[0m",
                    flush=True
                )
            else:
                print(
                    f"\x1b[1;31mFAIL\x1b[0m "
                    f"[{format_duration(elapsed):>10}] "
                    f"\x1b[0;35m{namespace['name']}::{test_class.name}\x1b[0m",
                    flush=True
                )
                failed = 1

    exit(failed)

if __name__ == "__main__":
    main()
