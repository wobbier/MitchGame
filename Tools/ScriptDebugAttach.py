#!/usr/bin/env python3
"""Attach a .NET debugger to Havana and hit a script breakpoint before and after a hot reload.

The scripted form of the "Attach to Havana (.NET)" session in Engine/Docs/Scripting-DotNet.md
(IDE integration): Havana runs ScriptTest.lvl with Tools/ScriptDebugAttach.edscript, netcoredbg
(the open-source coreclr debugger, MI mode) attaches to the running editor and sets one breakpoint
in HotReloadProbe.OnUpdate. Each hit reads the `version` local (1 before the reload, 3 after, so
the second hit is in the reloaded assembly) and writes Ticks, which opens the flow's next gate.

From the project root, after building Havana (editor_debug):
  Engine/Tools/NixEnv.sh python3 Tools/ScriptDebugAttach.py
netcoredbg comes from PATH or `nix build nixpkgs#netcoredbg`. The log lands in .tmp/ScriptDebugAttach.log.
"""
import argparse
import os
from pathlib import Path
import queue
import re
import shlex
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "Assets/Scripts/Tests/HotReloadProbe.cs"
BREAK_LINE = 13  # transform.Scale = ...: `version` is assigned, Ticks already incremented
# Hits before the reload, then after it: the `version` the code must show, the Ticks that opens the gate
EXPECTED_HITS = [("1", 1000000), ("3", 2000000)]


def host_env(**overrides):
    # The dev shell's LD_LIBRARY_PATH (newer glibc builds) breaks host tools like nix and netcoredbg
    env = {key: value for key, value in os.environ.items() if key != "LD_LIBRARY_PATH"}
    env.update(overrides)
    return env


def find_netcoredbg(explicit):
    if explicit:
        return explicit
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(directory) / "netcoredbg"
        if candidate.is_file():
            return str(candidate)
    out = subprocess.run(["nix", "--extra-experimental-features", "nix-command flakes", "build", "--no-link",
                          "--print-out-paths", "nixpkgs#netcoredbg"],
                         capture_output=True, text=True, check=True, env=host_env()).stdout.split()
    return str(Path(out[-1]) / "bin/netcoredbg")


def find_editor_pid(root_pid, timeout):
    # The wrappers fork; the editor is the descendant process named Havana
    deadline = time.time() + timeout
    while time.time() < deadline:
        parents = {}
        for entry in Path("/proc").iterdir():
            if entry.name.isdigit():
                try:
                    stat = (entry / "stat").read_text()
                    parents[int(entry.name)] = (stat[stat.index("(") + 1:stat.rindex(")")], int(stat[stat.rindex(")") + 2:].split()[1]))
                except (OSError, ValueError):
                    pass
        for pid, (name, _) in parents.items():
            ancestor = pid
            while ancestor in parents and ancestor != root_pid:
                ancestor = parents[ancestor][1]
            if name == "Havana" and ancestor == root_pid:
                return pid
        time.sleep(0.2)
    raise RuntimeError("Havana didn't start")


def wait_for_runtime(pid, timeout):
    # Attach needs CoreCLR loaded (the editor hosts it through hostfxr at script init)
    deadline = time.time() + timeout
    while time.time() < deadline:
        if "libcoreclr.so" in Path(f"/proc/{pid}/maps").read_text():
            return
        time.sleep(0.2)
    raise RuntimeError("the .NET runtime never loaded in Havana (is scripting enabled in this build?)")


class MiDebugger:
    def __init__(self, command, env, transcript):
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT, text=True, env=env)
        self.transcript = transcript
        self.events = queue.Queue()
        self.results = queue.Queue()
        self.token = 0
        threading.Thread(target=self.read, daemon=True).start()

    def read(self):
        for line in self.process.stdout:
            line = line.rstrip("\n")
            self.transcript.write(f"<- {line}\n")
            if re.match(r"^\d+\^", line):
                self.results.put(line)
            elif line.startswith(("*", "=")):
                self.events.put(line)
        self.events.put(None)

    def command(self, text, timeout=60):
        self.token += 1
        self.transcript.write(f"-> {self.token}{text}\n")
        self.process.stdin.write(f"{self.token}{text}\n")
        self.process.stdin.flush()
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                line = self.results.get(timeout=1)
            except queue.Empty:
                continue
            if line.startswith(f"{self.token}^"):
                return line
        raise RuntimeError(f"no answer to {text}")

    def evaluate(self, thread, expression):
        answer = self.command(f'-var-create --thread {thread} --frame 0 - * "{expression}"')
        name, value = mi_field(answer, "name"), mi_field(answer, "value")
        if name is None:
            raise RuntimeError(f"can't evaluate {expression}: {answer}")
        return name, value


def mi_field(line, key):
    match = re.search(rf'\b{key}="((?:[^"\\]|\\.)*)"', line)
    return match.group(1) if match else None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--editor", default=".build/Editor_Debug/Havana")
    parser.add_argument("--wrapper", default="Engine/Tools/Headless.sh")
    parser.add_argument("--netcoredbg", default="", help="debugger binary (default: PATH, then nixpkgs)")
    parser.add_argument("--timeout", type=int, default=900, help="seconds for the whole session")
    args = parser.parse_args()

    os.chdir(ROOT)
    log_dir = ROOT / ".tmp"
    log_dir.mkdir(exist_ok=True)
    original_probe = PROBE.read_bytes()
    debugger_binary = find_netcoredbg(args.netcoredbg)
    command = shlex.split(args.wrapper) + [args.editor, "--scene", "Assets/Scenes/Tests/ScriptTest.lvl",
                                           "--editor-exec", "Tools/ScriptDebugAttach.edscript"]
    editor = debugger = None
    hits = []
    loads = []
    with open(log_dir / "ScriptDebugAttach.log", "w") as editor_log, \
         open(log_dir / "ScriptDebugAttach.mi.log", "w", buffering=1) as transcript:
        try:
            editor = subprocess.Popen(command, stdout=editor_log, stderr=subprocess.STDOUT)
            deadline = time.time() + args.timeout
            pid = find_editor_pid(editor.pid, 60)
            wait_for_runtime(pid, 300)
            # The debugger finds the runtime's debug pipes under the editor's TMPDIR
            editor_env = dict(entry.split("=", 1) for entry in Path(f"/proc/{pid}/environ").read_text().split("\0") if "=" in entry)
            env = host_env(TMPDIR=editor_env.get("TMPDIR", "/tmp"))
            debugger = MiDebugger([debugger_binary, "--interpreter=mi"], env, transcript)

            print(f"attaching {Path(debugger_binary).name} to Havana (pid {pid})")
            answer = debugger.command(f"-target-attach {pid}")
            if "^error" in answer:
                raise RuntimeError(f"attach failed: {answer}")
            answer = debugger.command(f'-break-insert -f -c "Ticks >= 5 && Ticks < 1000000" {PROBE.name}:{BREAK_LINE}')
            if "^error" in answer:
                raise RuntimeError(f"breakpoint failed: {answer}")
            debugger.command("-exec-continue")  # an ^error just means it was already running

            while len(hits) < len(EXPECTED_HITS):
                remaining = deadline - time.time()
                if remaining <= 0 or editor.poll() is not None:
                    raise RuntimeError(f"{len(hits)} of {len(EXPECTED_HITS)} breakpoint hits before "
                                       + ("the timeout" if remaining <= 0 else "the editor exited"))
                try:
                    event = debugger.events.get(timeout=min(remaining, 5))
                except queue.Empty:
                    continue
                if event is None:
                    raise RuntimeError("netcoredbg exited")
                if event.startswith("=library-loaded") and "Game.Script" in (mi_field(event, "name") or ""):
                    loads.append(mi_field(event, "name"))
                if not event.startswith("*stopped"):
                    continue
                if mi_field(event, "reason") != "breakpoint-hit":
                    debugger.command("-exec-continue")
                    continue
                thread = mi_field(event, "thread-id")
                where = f"{Path(mi_field(event, 'fullname') or '?').name}:{mi_field(event, 'line')}"
                expected_version, ticks = EXPECTED_HITS[len(hits)]
                version_var, version = debugger.evaluate(thread, "version")
                ticks_var, before = debugger.evaluate(thread, "Ticks")
                debugger.command(f"-var-assign {ticks_var} {ticks}")
                debugger.command(f"-var-delete {version_var}")
                debugger.command(f"-var-delete {ticks_var}")
                hits.append(version)
                print(f"hit {len(hits)} at {where}: version = {version}, Ticks = {before} -> {ticks}")
                if version is None or float(version) != float(expected_version):
                    raise RuntimeError(f"hit {len(hits)} ran version {version}, expected {expected_version}")
                debugger.command("-exec-continue")

            # Both hits done: the flow restores the probe, reloads and quits
            code = editor.wait(timeout=max(1, deadline - time.time()))
            editor_log.flush()
            text = (log_dir / "ScriptDebugAttach.log").read_text(errors="replace")
            for line in re.findall(r"\[editor-exec\] FAIL[^\n]*", text)[:8]:
                print(f"    {line}")
            passed = "[editor-exec] PASSED" in text and code == 0
            print(f"Game.Script loads seen by the debugger: {len(loads)}")
            print(("PASSED" if passed else "FAILED") + ": breakpoint hit before and after a hot reload"
                  + ("" if passed else " (see .tmp/ScriptDebugAttach.log)"))
            return 0 if passed else 1
        except (RuntimeError, subprocess.TimeoutExpired) as error:
            print(f"FAILED: {error} (see .tmp/ScriptDebugAttach.log and .tmp/ScriptDebugAttach.mi.log)")
            return 1
        finally:
            if debugger and debugger.process.poll() is None:
                debugger.process.kill()
            if editor and editor.poll() is None:
                editor.kill()
                subprocess.run(["pkill", "-x", "Havana"])
            if PROBE.read_bytes() != original_probe:
                PROBE.write_bytes(original_probe)


if __name__ == "__main__":
    sys.exit(main())
