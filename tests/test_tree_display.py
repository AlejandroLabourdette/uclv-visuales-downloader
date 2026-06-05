from unittest.mock import MagicMock

from uclv_visuales_downloader.tree_display import DownloadDisplay, _parent_path, _fmt_size


def make_display():
    d = DownloadDisplay()
    d._live = MagicMock()
    return d


# --- _parent_path ---

def test_parent_path_root_returns_none():
    assert _parent_path("MyDir/") is None


def test_parent_path_one_level():
    assert _parent_path("Root/Child/") == "Root/"


def test_parent_path_two_levels():
    assert _parent_path("Root/Child/Leaf/") == "Root/Child/"


# --- on_directory_entered ---

def test_creates_node_on_entry():
    d = make_display()
    d.on_directory_entered("MyDir/", 5, [])
    assert "MyDir/" in d._nodes
    node = d._nodes["MyDir/"]
    assert node.name == "MyDir"
    assert node.file_count == 5
    assert node.status == "in_progress"


def test_adds_to_roots():
    d = make_display()
    d.on_directory_entered("MyDir/", 0, [])
    assert "MyDir/" in d._roots


def test_adds_children_as_unexplored():
    d = make_display()
    d.on_directory_entered("Root/", 5, ["Child1/", "Child2/"])
    assert "Root/Child1/" in d._nodes
    assert "Root/Child2/" in d._nodes
    assert d._nodes["Root/Child1/"].status == "unexplored"
    assert d._nodes["Root/"].children_paths == ["Root/Child1/", "Root/Child2/"]


def test_child_name_stripped_of_slash():
    d = make_display()
    d.on_directory_entered("Root/", 0, ["My Season/"])
    assert d._nodes["Root/My Season/"].name == "My Season"


def test_sets_current_path():
    d = make_display()
    d.on_directory_entered("Root/", 3, [])
    assert d._current_path == "Root/"


def test_empty_dir_becomes_complete():
    d = make_display()
    d.on_directory_entered("Root/", 0, [])
    assert d._nodes["Root/"].status == "complete"


def test_second_entry_updates_existing_node():
    d = make_display()
    d.on_directory_entered("Root/", 0, ["Child/"])
    d.on_directory_entered("Root/Child/", 3, [])
    assert d._nodes["Root/Child/"].file_count == 3
    assert d._nodes["Root/Child/"].status == "in_progress"
    # child should not be added to roots
    assert "Root/Child/" not in d._roots


# --- on_file_done ---

def test_file_done_increments_count():
    d = make_display()
    d.on_directory_entered("Root/", 3, [])
    d.on_file_done("Root/")
    assert d._nodes["Root/"].files_done == 1


def test_file_done_completes_directory():
    d = make_display()
    d.on_directory_entered("Root/", 2, [])
    d.on_file_done("Root/")
    d.on_file_done("Root/")
    assert d._nodes["Root/"].status == "complete"


def test_file_done_clears_current_file():
    d = make_display()
    d.on_directory_entered("Root/", 1, [])
    d.on_file_start("file.mp4", 1000)
    assert d._current_file is not None
    d.on_file_done("Root/")
    assert d._current_file is None


def test_file_done_ignores_unknown_path():
    d = make_display()
    d.on_file_done("nonexistent/")  # should not raise


# --- completion bubble-up ---

def test_completion_bubbles_to_parent():
    d = make_display()
    d.on_directory_entered("Root/", 0, ["Child/"])
    d.on_directory_entered("Root/Child/", 1, [])
    d.on_file_done("Root/Child/")
    assert d._nodes["Root/Child/"].status == "complete"
    assert d._nodes["Root/"].status == "complete"


def test_parent_stays_in_progress_with_unexplored_sibling():
    d = make_display()
    d.on_directory_entered("Root/", 0, ["Child1/", "Child2/"])
    d.on_directory_entered("Root/Child1/", 1, [])
    d.on_file_done("Root/Child1/")
    assert d._nodes["Root/Child1/"].status == "complete"
    assert d._nodes["Root/"].status == "in_progress"


def test_parent_completes_after_both_children_done():
    d = make_display()
    d.on_directory_entered("Root/", 0, ["Child1/", "Child2/"])
    d.on_directory_entered("Root/Child1/", 1, [])
    d.on_directory_entered("Root/Child2/", 1, [])
    d.on_file_done("Root/Child1/")
    assert d._nodes["Root/"].status == "in_progress"
    d.on_file_done("Root/Child2/")
    assert d._nodes["Root/"].status == "complete"


# --- _get_active_path_set ---

def test_active_path_set_root_only():
    d = make_display()
    d.on_directory_entered("Root/", 1, [])
    active = d._get_active_path_set()
    assert active == {"Root/"}


def test_active_path_set_includes_ancestors():
    d = make_display()
    d.on_directory_entered("Root/", 0, ["Child/"])
    d.on_directory_entered("Root/Child/", 0, ["Leaf/"])
    d.on_directory_entered("Root/Child/Leaf/", 1, [])
    active = d._get_active_path_set()
    assert "Root/" in active
    assert "Root/Child/" in active
    assert "Root/Child/Leaf/" in active


def test_active_path_empty_when_no_current():
    d = make_display()
    assert d._get_active_path_set() == set()


# --- _fmt_size ---

def test_fmt_size_bytes():
    assert _fmt_size(500) == "500.0 B"


def test_fmt_size_kilobytes():
    assert _fmt_size(2048) == "2.0 KB"


def test_fmt_size_megabytes():
    assert _fmt_size(5 * 1024 * 1024) == "5.0 MB"
