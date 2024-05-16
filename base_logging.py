import datetime
from json import JSONEncoder
from time import sleep

from loguru import logger
from rich.console import Console
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.progress import Progress
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return JSONEncoder.default(self, obj)


class Logger:
    def __init__(self):
        self.console = Console()
        self.console_utils = ConsoleUtils()
        logger.remove()
        logger.add(
            RichHandler(console=self.console, markup=True),
            format="{message}",
            level="DEBUG",
        )

    def log_exception(self, exception):
        self.console.print("❌", f"[bold red]Exception: {exception}[/bold red]")
        logger.exception(exception)

    def log_warning(self, warning):
        self.console.print("⚠️", f"[bold yellow]Warning: {warning}[/bold yellow]")

    def log_error(self, error):
        self.console.print("❌", f"[bold red]Error: {error}[/bold red]")

    def log_success(self, success):
        self.console.print("✅", f"[bold green]Success: {success}[/bold green]")

    def log_failure(self, failure):
        self.console.print("❌", f"[bold red]Failure: {failure}[/bold red]")

    def log_debug(self, debug):
        self.console.print("🐞", f"[bold blue]Debug: {debug}[/bold blue]")

    def log_critical(self, critical):
        self.console.print("🚨", f"[bold red]Critical: {critical}[/bold red]")

    def log_info(self, info, **kwargs):
        self.console.print("ℹ️", f"[bold blue]Info: {info}[/bold blue]")
        logger.bind(**kwargs).info(info)

    def log_trace(self, trace):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.console.print(
            "🔍",
            f"[bold blue]{timestamp}[/bold blue] - [bold blue]Trace: {trace}[/bold blue]",
        )
        logger.trace(f"{timestamp} - Trace: {trace}")

    def configure_logging(self):
        logger.info("Logging configured")
        self.console_utils.log_progress("Logging", 100, 100)
        self.log_success("Logging configured successfully")

    def set_level(self, level):
        logger.level(level)
        self.console_utils.log_progress("Log Level", 100, 100)
        self.log_success(f"Log level set to {level}")


class ConsoleUtils:
    def __init__(self):
        self.console = Console()

    def log_tasks(self, tasks):
        with self.console.status(
            "[bold green]Working on tasks...", spinner="dots2"
        ) as status:
            for task_name, task_func in tasks:
                sleep(1)
                self.console.log(f"{task_name} complete")

    def log_table(self, data, title="Table", caption="", **kwargs):
        table = Table(title=title, caption=caption, **kwargs)
        for header, values in data.items():
            table.add_column(header, justify="center", style="cyan")
            for value in values:
                table.add_row(*[str(v) for v in value])
        self.console.print("📊", table)

    def log_progress(self, task_description, completed, total):
        with Progress() as progress:
            task = progress.add_task(task_description, total=total)
            while not progress.finished:
                progress.update(task, advance=completed)
        self.console.print("⏳", f"Progress: {task_description} - {completed}/{total}")

    def log_markdown(self, data):
        markdown = Markdown(data)
        self.console.print("📝", markdown)

    def log_syntax_highlighting(self, code, language="python"):
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        self.console.print("🖥️", syntax)

    def log_tree(self, data, parent=None, indent=0):
        for key, value in data.items():
            if isinstance(value, dict):
                node = Tree(f"[cyan]{key}[/cyan]")
                self.log_tree(value, node, indent + 1)
                if parent is None:
                    self.console.print("🌳", node)
                else:
                    parent.add(node)
            else:
                if parent is None:
                    self.console.print("🌳", f"[cyan]{key}[/cyan]")
                else:
                    parent.add(f"[cyan]{key}[/cyan]")
