from __future__ import annotations

import sys
import time
from pathlib import Path

import runpy
from _pytest.capture import CaptureFixture
from rtf import RTF, main


def write_rtf(path: Path, text: str) -> None:
    path.write_text("{\\rtf1\n\n" + text + "}", encoding="latin-1")


def test_to_plain_text(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.rtf"
    write_rtf(file_path, "Hello!")
    assert RTF.to_plain_text(str(file_path)) == "Hello!"


def test_plain_text_caching(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.rtf"
    write_rtf(file_path, "Hi")
    rtf_obj = RTF(str(file_path))
    first = rtf_obj.plain_text()
    assert first == "Hi"

    time.sleep(1)
    write_rtf(file_path, "New")
    second = rtf_obj.plain_text()
    assert second == "New"


def test_dump(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.rtf"
    write_rtf(file_path, "Data")
    output = tmp_path / "out.txt"
    rtf_obj = RTF(str(file_path))
    assert rtf_obj.dump(str(output)) is True
    assert output.read_text(encoding="latin-1") == "Data"


def test_dump_failure(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.rtf"
    write_rtf(file_path, "Data")
    rtf_obj = RTF(str(file_path))
    output = tmp_path / "nonexistent" / "out.txt"
    assert rtf_obj.dump(str(output)) is False


def test_main_prints_plain_text(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    file_path = tmp_path / "sample.rtf"
    write_rtf(file_path, "Main")
    sys.argv = ["rtf.py", str(file_path)]
    main()
    captured = capsys.readouterr()
    assert captured.out == "Main\n"


def test_main_dump(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.rtf"
    output = tmp_path / "out.txt"
    write_rtf(file_path, "Dump")
    sys.argv = ["rtf.py", str(file_path), str(output)]
    main()
    assert output.read_text(encoding="latin-1") == "Dump"


def test_escaped_sequences(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.rtf"
    content = "\\\\a " + "\\\\\n" + "END"
    write_rtf(file_path, content)
    assert RTF.to_plain_text(str(file_path)) == "\nEND"


def test_run_as_script(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    file_path = tmp_path / "sample.rtf"
    write_rtf(file_path, "Script")
    sys.argv = ["rtf.py", str(file_path)]
    runpy.run_module("rtf", run_name="__main__")
    captured = capsys.readouterr()
    assert captured.out == "Script\n"
