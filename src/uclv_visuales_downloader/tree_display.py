from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from rich.console import Console, Group
from rich.live import Live
from rich.text import Text


@dataclass
class _DirNode:
    name: str
    path: str
    parent_path: Optional[str]
    children_paths: list = field(default_factory=list)
    file_count: int = 0
    files_done: int = 0
    status: str = "unexplored"  # "unexplored" | "in_progress" | "complete"


@dataclass
class _FileProgress:
    filename: str
    total_size: int
    downloaded: int
    start_time: float


class DownloadDisplay:
    def __init__(self):
        self._nodes: dict = {}
        self._roots: list = []
        self._current_path: Optional[str] = None
        self._current_file: Optional[_FileProgress] = None
        self._live = Live(Text(""), console=Console(stderr=True), refresh_per_second=4)

    def __enter__(self) -> DownloadDisplay:
        self._live.__enter__()
        return self

    def __exit__(self, *args):
        self._live.update(self._render())
        self._live.__exit__(*args)

    def on_directory_entered(self, path: str, file_count: int, subdir_hrefs: list):
        """Called by link_finder when a directory page is fetched.

        subdir_hrefs: list of decoded subdir names with trailing slash, e.g. ["Season 1/"]
        """
        node = self._get_or_create_node(path)
        node.file_count = file_count
        node.status = "in_progress"

        for href in subdir_hrefs:
            child_path = path + href
            if child_path not in self._nodes:
                child_name = href.rstrip("/")
                child = _DirNode(name=child_name, path=child_path, parent_path=path)
                self._nodes[child_path] = child
                node.children_paths.append(child_path)

        self._current_path = path
        self._try_complete(path)
        self._live.update(self._render())

    def on_file_start(self, filename: str, total_size: int, initial: int = 0):
        self._current_file = _FileProgress(
            filename=filename,
            total_size=total_size,
            downloaded=initial,
            start_time=time.monotonic(),
        )
        self._live.update(self._render())

    def on_file_progress(self, n_bytes: int):
        if self._current_file:
            self._current_file.downloaded += n_bytes
            self._live.update(self._render())

    def on_file_done(self, path: str):
        node = self._nodes.get(path)
        if node:
            node.files_done += 1
        self._current_file = None
        self._try_complete(path)
        self._live.update(self._render())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_or_create_node(self, path: str) -> _DirNode:
        if path not in self._nodes:
            parts = path.split("/")
            name = parts[-2] if len(parts) >= 2 else path
            parent = _parent_path(path)
            node = _DirNode(name=name, path=path, parent_path=parent)
            self._nodes[path] = node
            if parent is None:
                self._roots.append(path)
        return self._nodes[path]

    def _try_complete(self, path: str):
        node = self._nodes.get(path)
        if not node or node.status in ("complete", "unexplored"):
            return
        if node.files_done >= node.file_count and all(
            self._nodes[cp].status == "complete" for cp in node.children_paths
        ):
            node.status = "complete"
            if node.parent_path:
                self._try_complete(node.parent_path)

    def _get_active_path_set(self) -> set:
        if not self._current_path:
            return set()
        result = set()
        path = self._current_path
        while path:
            result.add(path)
            node = self._nodes.get(path)
            if not node or node.parent_path is None:
                break
            path = node.parent_path
        return result

    def _render(self):
        lines = []
        active_set = self._get_active_path_set()
        for root_path in self._roots:
            self._render_node(root_path, active_set, lines, 0)
        return Group(*lines) if lines else Text("")

    def _render_node(self, path: str, active_set: set, lines: list, indent: int):
        node = self._nodes.get(path)
        if not node:
            return

        prefix = "    " * indent

        if node.status == "complete":
            style = "green"
            suffix = " (Completed)"
        elif node.status == "in_progress":
            style = "yellow"
            suffix = (
                f" ({node.files_done}/{node.file_count})"
                if node.file_count > 0
                else " (In Progress)"
            )
        else:
            style = "white"
            suffix = ""

        lines.append(Text(prefix + node.name + suffix, style=style))

        if path == self._current_path and self._current_file:
            lines.append(self._render_file_bar(indent + 1))

        if path in active_set:
            for child_path in node.children_paths:
                self._render_node(child_path, active_set, lines, indent + 1)

    def _render_file_bar(self, indent: int) -> Text:
        prefix = "    " * indent
        cf = self._current_file
        if cf.total_size > 0:
            pct = min(100, int(cf.downloaded * 100 / cf.total_size))
            bar_width = 25
            filled = int(bar_width * pct / 100)
            bar = "#" * filled + " " * (bar_width - filled)
            elapsed = time.monotonic() - cf.start_time
            speed_str = ""
            if elapsed > 0.5:
                speed_str = f" | {_fmt_size(cf.downloaded / elapsed)}/s"
            size_str = f"{_fmt_size(cf.downloaded)}/{_fmt_size(cf.total_size)}"
            return Text(
                f"{prefix}[{bar}] {pct}%  {size_str}{speed_str}  {cf.filename}",
                style="orange3",
            )
        return Text(
            f"{prefix}↓ {cf.filename} ({_fmt_size(cf.downloaded)})", style="orange3"
        )


def _parent_path(path: str) -> Optional[str]:
    parts = path.split("/")
    if len(parts) <= 2:  # root: ["Name", ""]
        return None
    return "/".join(parts[:-2]) + "/"


def _fmt_size(size: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
