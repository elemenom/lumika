try:
    import logging, os
    from getpass import getpass
    from subprocess import run
    from sys import argv
    from typing import Any, Callable
    from prompt_toolkit import PromptSession
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.completion import WordCompleter

    def paint(cont: str) -> str:
        return cont \
            .replace("&bold", "\033[1m") \
            .replace("&underline", "\033[4m") \
            .replace("&italic", "\033[3m") \
            .replace("&blink", "\033[5m") \
            .replace("&reverse", "\033[7m") \
            .replace("&hide", "\033[8m") \
            .replace("&reset", "\033[0m") \
            .replace("&g", "\033[32m") \
            .replace("&r", "\033[31m") \
            .replace("&y", "\033[33m") \
            .replace("&b", "\033[34m") \
            .replace("&m", "\033[35m") \
            .replace("&c", "\033[36m") \
            .replace("&w", "\033[37m") \
            .replace("&0", "\033[0m") \
            + "\033[0m"

    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s: %(message)s"
    )

    class ColoredFormatter(logging.Formatter):
        COLORS: dict[str, str] = {
            "DEBUG": "&c",
            "INFO": "&g",
            "WARNING": "&y",
            "ERROR": "&r",
            "CRITICAL": "&m"
        }

        def format(self, record) -> str:
            levelname = record.levelname
            if levelname in self.COLORS:
                levelname = record.levelname.lower()  # Use lowercase
                colored_msg = f"{self.COLORS[record.levelname]}{record.msg}&0"  # Add color
                record.msg = colored_msg
                record.levelname = levelname

            return paint(super().format(record))

    logger: logging.Logger = logging.getLogger(__name__)
    handler: logging.StreamHandler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter("%(levelname)s: %(message)s"))
    logger.handlers = []
    logger.addHandler(handler)
    logger.propagate = False
    autocomplete_words: list[str] = [
        "cd ", "cm ", "ls ",
        "dir ", "pwd ", "mkdir ",
        "rmdir ", "rm ", "mv ",
        "cp ", "cls ", "cat ",
        "echo ", "type ", "more ",
        "less ", "nano ", "vim ",
        "vi ", "head ", "tail ",
        "touch ", "clear ", "history ",
        "kill ", "tasklist ", "ps ",
        "top ", "htop ", "uname ",
        "hostname ", "df ", "du ",
        "free ", "systeminfo ", "date ",
        "uptime ", "ping ", "tracert ",
        "traceroute ", "ipconfig ", "ifconfig ",
        "netstat ", "nslookup ", "curl ",
        "wget ", "chmod ", "chown ",
        "tar ", "zip ", "unzip ",
        "gzip ", "gunzip ", "apt ",
        "apt-get ", "yum ", "dnf ",
        "brew ", "pip ", "choco ",
        "exit ", "man ", "help ",
        "alias ", "source ", "./ ",
        "python ", "node ", "perl ",
        "ruby ", "whoami ", "sudo ",
        "shutdown ", "reboot ", "get-command ",
        "get-help ", "get-process ", "set-location ",
        "copy-item ", "remove-item ", "start-process ",
        "stop-process ", "invoke-webrequest ", "new-item ",
        "for ", "while ", "if ",
        "&& ", "| ", "> ",
        ">> ", "ca ", "set ",
        "python -m ", "{ ", "start ",
        "npm ", "cargo ", "verbose ",
        "cm : ", "cm .. ", "cd c:/ ",
        "git commit -m \"", "git ", "git add --all "
        "git push --all ", "git add ", "python main.py "
        "git push ", "git init ", "cm :pwsh.exe ",
        "cm :cmd.exe ", "sudo ", "sudo apt ",
        "pip install ", "pip uninstall ", "pip show ",
        "}"
    ]
    history: InMemoryHistory = InMemoryHistory()
    completer: WordCompleter = WordCompleter(autocomplete_words, ignore_case=True)
    session: PromptSession = PromptSession(history=history, completer=completer)
    enter_to_continue: Callable = lambda: getpass(paint("\n\n\n&c&bold""   -press enter to continue-"))
    prompt: Callable[[list[str]], str] = lambda launcher: (f"<ansiyellow><b>{os.environ.get("USERNAME", "Guest")}</b></ansiyellow>~"
        f"<ansiblue><i>{os.getcwd().replace("\\", "/")}</i></ansiblue>:"
        f"<ansired>{"/".join(launcher)}</ansired>> ")

    def get(l: list[Any], index: int, default: Any = None) -> Any:
        try:
            return l[index]

        except IndexError:
            l.append(default)

            return get(l, index, default)

    def lumika_run(launcher: list[str], cmd: str, verbose: bool = False) -> None:
        log = lambda cont: logger.debug(cont) if verbose else None

        try:
            try:
                with open(".ATOMIC") as file:
                    var_list: dict[str, str] = eval("{" + file.read() + "}")

            except FileNotFoundError:
                var_list: dict[str, str] = {}

            full_cmd = f"{" ".join(launcher)} {cmd}".format(**var_list)
            log(f"running '{full_cmd}'")

            os.system(full_cmd)

        except KeyError as err:
            logger.error(f"fetch request failed: no variable {str(err)}")

            return

        log("process terminated")

    def lumika_multi(launcher: list[str]) -> list[str]:
        cmds: list[str] = []

        while True:
            cmd: str = session.prompt(HTML(prompt(launcher)[:-1] + "<ansiyellow>:</ansiyellow>")).split(";")

            for c in cmd:
                if c == "}":
                    return cmds

                cmds.append(c)

    def lumika_parse(launcher: list[str], cmd: str, clear: bool = True) -> list[str]:
        cmd = cmd.strip()

        if cmd == "":
            ...

        elif cmd == "exit":
            print("exited lumika")

            exit()

        elif cmd == "ca":
            print("are you sure you want to clear all atomic variables in this directory?")
            print("this cannot be undone.")
            while True:
                confirm: str = input("y/n: ").lower()

                if confirm == "y":
                    try:
                        os.remove(".ATOMIC")

                    except FileNotFoundError:
                        ...

                    print("atomic variables cleared")
                    break

                elif confirm == "n":
                    break

                else:
                    print("invalid input")

        elif cmd == "{":
            m_cmds: list[str] = lumika_multi(launcher)

            for m_cmd in m_cmds:
                lumika_parse(launcher, m_cmd, False)

            if clear: enter_to_continue()

        elif cmd.startswith("set "):
            cmd = cmd.removeprefix("set ")
            parts: list[str] = cmd.split("=")

            if len(parts) == 1:
                logger.error("too few arguments")

            else:
                with open(".ATOMIC", "a") as file:
                    file.write(f"\"{parts[0].strip()}\": \"{parts[1].strip().strip("\"")}\",\n")

                print(f"set atomic variable '{parts[0].strip()}' to '{parts[1].strip().strip("\"")}'")

            if clear: enter_to_continue()

        elif cmd == "set":
            logger.error("too few arguments")

            if clear: enter_to_continue()

        elif cmd.startswith("verbose "):
            lumika_run(launcher, cmd.removeprefix("verbose "), True)

            if clear: enter_to_continue()

        elif cmd == "verbose":
            logger.error("too few arguments")

            if clear: enter_to_continue()

        elif cmd.startswith("cm :"):
            launcher = cmd.removeprefix("cm :").split("/")

            print(f"changed current working module to '{"/".join(launcher)}'")
            if clear: enter_to_continue()

        elif cmd.startswith("cm "):
            for c in cmd.removeprefix("cm ").split("/"):
                if c == ".." and len(launcher) != 0:
                    pop: str = launcher.pop()

                    if pop == "-Command":
                        launcher.pop()

                    elif pop == "/C":
                        launcher.pop()

                else:
                    launcher.append(c)

            print(f"changed current working module to '{"/".join(launcher)}'")

            if clear: enter_to_continue()

        elif cmd == "cm":
            logger.error("too few arguments")

            if clear: enter_to_continue()

        elif cmd == "reboot":
            print("restarted lumika")
            if clear: enter_to_continue()
            os.system("clear")
            run(["python.exe", "-m", "lumika"])
            exit()

        elif cmd.startswith("cd "):
            try:
                os.chdir(cmd.removeprefix("cd "))

                print(f"changed working directory to '{os.getcwd()}'")

            except FileNotFoundError:
                logger.error(f"directory '{cmd.removeprefix('cd ')}' not found in '{os.getcwd()}'")

            if clear: enter_to_continue()

        elif cmd == "cd":
            logger.error("too few arguments")

            if clear: enter_to_continue()

        else:
            lumika_run(launcher, cmd)

            if clear: enter_to_continue()

        if clear:
            os.system("clear")

        return launcher

    def lumika_std() -> None:
        os.system("clear")
        launcher: list[str] = argv[1].split("/") if len(argv) > 1 else ["cmd.exe"]

        while True:
            for i, _ in enumerate(launcher):
                if launcher[i] in [
                    "pwsh",
                    "pwsh.exe"
                ]:
                    if get(launcher, i + 1, "-Command") != "-Command":
                        launcher.insert(i + 1, "-Command")

                elif launcher[i] in [
                    "cmd",
                    "cmd.exe"
                ]:
                    if get(launcher, i + 1, "/C") != "/C":
                        launcher.insert(i + 1, "/C")

            try:
                launcher.pop(0) if launcher[0] == "" else None

            except IndexError:
                ...

            try:
                cmds: list[str] = session.prompt(HTML(prompt(launcher))).split(";")

                for cmd in cmds:
                    launcher = lumika_parse(launcher, cmd)

            except EOFError:
                ...

    if __name__ == "__main__":
        lumika_std()

except KeyboardInterrupt:
    print("^C")