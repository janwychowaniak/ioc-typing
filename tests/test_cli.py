"""Tests for the ioc-classify CLI."""

import io
import json

from ioc_typing._cli import main


def test_classify_file_tsv(tmp_path, capsys):
    iocs = tmp_path / "iocs.txt"
    iocs.write_text("8.8.8.8\nexample.com\n", encoding="utf-8")

    rc = main([str(iocs)])
    assert rc == 0

    out = capsys.readouterr().out.splitlines()
    assert out[0] == "query\tdetermined\ttype_pri\ttype_sec"
    assert out[1] == "8.8.8.8\tTrue\tip\tv4"
    assert out[2] == "example.com\tTrue\tdomain\t-"


def test_classify_file_json(tmp_path, capsys):
    iocs = tmp_path / "iocs.txt"
    iocs.write_text("8.8.8.8\n", encoding="utf-8")

    rc = main([str(iocs), "--format", "json"])
    assert rc == 0

    line = capsys.readouterr().out.strip()
    assert json.loads(line) == {
        "query": "8.8.8.8",
        "determined": True,
        "type_pri": "ip",
        "type_sec": "v4",
    }


def test_classify_skips_blank_and_comment_lines(tmp_path, capsys):
    iocs = tmp_path / "iocs.txt"
    iocs.write_text("# comment\n\n8.8.8.8\n  \n", encoding="utf-8")

    rc = main([str(iocs)])
    assert rc == 0

    body = capsys.readouterr().out.splitlines()[1:]  # drop header
    assert body == ["8.8.8.8\tTrue\tip\tv4"]


def test_classify_file_not_found(tmp_path, capsys):
    rc = main([str(tmp_path / "missing.txt")])
    assert rc == 1
    assert "error" in capsys.readouterr().err


def test_classify_stdin(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("8.8.8.8\n"))
    rc = main([])
    assert rc == 0

    out = capsys.readouterr().out.splitlines()
    assert out[1] == "8.8.8.8\tTrue\tip\tv4"


def test_classify_stdin_dash(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO("8.8.8.8\n"))
    rc = main(["-"])
    assert rc == 0

    out = capsys.readouterr().out.splitlines()
    assert out[1] == "8.8.8.8\tTrue\tip\tv4"


def test_classify_handles_broken_pipe(tmp_path, monkeypatch):
    # Simulate a downstream consumer (e.g. `| head`) closing its stdin.
    # The CLI must exit 0 instead of letting the traceback leak out.
    iocs = tmp_path / "iocs.txt"
    iocs.write_text("8.8.8.8\n", encoding="utf-8")

    def raise_broken_pipe(*_args, **_kwargs):
        raise BrokenPipeError()

    monkeypatch.setattr("ioc_typing._cli._emit_tsv", raise_broken_pipe)
    # Stub the dup2 redirect so it doesn't disturb pytest's capture.
    monkeypatch.setattr("ioc_typing._cli._suppress_remaining_output", lambda: None)

    assert main([str(iocs)]) == 0
