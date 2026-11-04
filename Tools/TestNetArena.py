#!/usr/bin/env python3
"""Headless smoke test for the NetArena multiplayer sample (issue board #9 / #30).

Hosts Assets/Scenes/NetArena.lvl on a free UDP port (the game build, or the headless Server build
with --server-game), joins two autopiloted clients (Game.NetPawnAutoPilot = 1 in their user://
Settings.json makes NetPawn walk forward and jump once) and checks the logs:
  server  : both pawns were handed to clients, both pawns moved
  clients : each owns a pawn, its autopilot moved it, and it saw the other pawn move

    Tools/TestNetArena.py                       # .build/Game_linux_Debug/Game_EntryPoint_x64 as server and clients
    Tools/TestNetArena.py --server-game .build/Server_linux_Debug/Game_EntryPoint_x64

Run from the game root inside the dev shell (Engine/Tools/DevShell.sh). Logs, reports and the
clients' captures land in --out (.tmp/NetArena). Exits 1 on failure.
"""
import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import time

SCENE = "Assets/Scenes/NetArena.lvl"


def read_text(path):
    try:
        with open(path, errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def wait_for_line(path, text, process, timeout):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if text in read_text(path):
            return True
        if process.poll() is not None:
            return text in read_text(path)
        time.sleep(0.25)
    return False


def wait_for_exit(process, timeout):
    try:
        process.wait(timeout=timeout)
        return True
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--game", default=".build/Game_linux_Debug/Game_EntryPoint_x64", help="client executable")
    parser.add_argument("--server-game", default="", help="server executable (default: the client one, windowed through --wrapper)")
    parser.add_argument("--wrapper", default="Engine/Tools/Headless.sh", help="command prefix for windowed processes")
    parser.add_argument("--frames", type=int, default=700, help="client frames before they leave")
    parser.add_argument("--host-timeout", type=float, default=300.0)
    parser.add_argument("--client-timeout", type=float, default=600.0)
    parser.add_argument("--net-args", default="", help="extra arguments for both sides, e.g. '--net-lag 40'")
    parser.add_argument("--out", default=".tmp/NetArena")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    wrapper = shlex.split(args.wrapper)
    net_args = shlex.split(args.net_args)
    server_game = args.server_game or args.game
    server_log = os.path.join(args.out, "server.log")
    backstop = int(60 * (args.host_timeout + args.client_timeout + 60))
    server_command = ([] if args.server_game else wrapper) + [server_game, "--scene", SCENE, "--server", "0", "--net-exit-when-empty",
        "--net-report", os.path.join(args.out, "server.json"), "--no-audio", "--no-profile-enforcement", "--frames", str(backstop)] + net_args
    print("server: " + " ".join(shlex.quote(p) for p in server_command))
    with open(server_log, "w") as log:
        server = subprocess.Popen(server_command, stdout=log, stderr=subprocess.STDOUT)
    clients = []
    failures = []
    try:
        if not wait_for_line(server_log, "Net: hosting on UDP port", server, args.host_timeout):
            print(f"FAIL  the server never started hosting (see {server_log})")
            return 1
        port = int(re.search(r"Net: hosting on UDP port (\d+)", read_text(server_log)).group(1))

        for i in (1, 2):
            user_dir = os.path.join(args.out, f"user{i}")
            os.makedirs(user_dir, exist_ok=True)
            with open(os.path.join(user_dir, "Settings.json"), "w") as settings:
                json.dump({"Version": 1, "Game": {"NetPawnAutoPilot": 1}}, settings)
            log_path = os.path.join(args.out, f"client{i}.log")
            command = wrapper + [args.game, "--scene", SCENE, "--connect", f"127.0.0.1:{port}", "--frames", str(args.frames),
                "--no-audio", "--no-profile-enforcement", "--user-dir", user_dir, "--screenshot", os.path.join(args.out, f"client{i}.png"),
                "--net-report", os.path.join(args.out, f"client{i}.json"), "--exit"] + net_args
            print(f"client {i}: " + " ".join(shlex.quote(p) for p in command))
            # Each wrapped client gets its own virtual display: Headless.sh stops the Xvfb it started
            # when its command exits, which would take a shared display away from the other client.
            environment = dict(os.environ, HEADLESS_DISPLAY=f":{120 + 10 * i}")
            with open(log_path, "w") as log:
                clients.append((i, log_path, subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True, env=environment)))
            # The second client joins once the first is in, so pawn 1 goes to client 1.
            if i == 1 and not wait_for_line(server_log, "NetPawn: pawn 1 -> client #", server, args.client_timeout):
                failures.append("the server never handed pawn 1 to the first client")

        for i, log_path, process in clients:
            if not wait_for_exit(process, args.client_timeout):
                failures.append(f"client {i} hung (killed)")
        if not wait_for_exit(server, 60):
            failures.append("the server did not exit once the clients left")

        server_text = read_text(server_log)
        for expected in ("NetPawn: pawn 1 -> client #", "NetPawn: pawn 2 -> client #", "NetPawn: pawn 1 moved", "NetPawn: pawn 2 moved"):
            if expected not in server_text:
                failures.append(f"server log lacks '{expected}'")
        for i, log_path, _ in clients:
            text = read_text(log_path)
            for expected in (f"NetPawn: pawn {i} is mine", "NetPawn: autopilot: own pawn moved", f"NetPawn: remote pawn {3 - i} moved"):
                if expected not in text:
                    failures.append(f"client {i} log lacks '{expected}'")
            if "autopilot FAILED" in text:
                failures.append(f"client {i}: autopilot FAILED")
            if "Assertion" in text or "Segmentation" in text:
                failures.append(f"client {i}: crashed or asserted")
        for side in ("server", "client1", "client2"):
            report = os.path.join(args.out, f"{side}.json")
            if not os.path.exists(report):
                failures.append(f"{side}: no --net-report")
    finally:
        for _, _, process in clients:
            if process.poll() is None:
                process.kill()
        if server.poll() is None:
            server.kill()

    for failure in failures:
        print("FAIL  " + failure)
    if failures:
        print(f"NetArena: FAILED ({len(failures)} problems; logs in {args.out})")
        return 1
    moved = re.findall(r"NetPawn: autopilot: own pawn moved ([0-9.]+) m, jumps (\d+), corrections (\d+)", "".join(read_text(l) for _, l, _ in clients))
    print(f"NetArena: PASSED (clients moved {', '.join(m[0] + ' m' for m in moved)}; jumps {', '.join(m[1] for m in moved)}; corrections {', '.join(m[2] for m in moved)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
