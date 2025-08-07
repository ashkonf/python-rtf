"""Simple utilities for converting RTF documents to plain text."""

from __future__ import annotations

import os
import sys
import time
from typing import Optional


class RTF:
    """Utility class for parsing RTF files."""

    @staticmethod
    def to_plain_text(file_name: str) -> str:
        """Return the plain text representation of ``file_name``."""

        text = ""
        ignoring_header = True
        last_char_was_newline = False
        escape = False
        control = ""
        param = ""
        hex_mode = False
        hex_buffer = ""
        brace_depth = 0

        with open(file_name, encoding="latin-1") as file:
            while True:
                char = file.read(1)
                if not char:
                    if escape or hex_mode or control or param:
                        raise ValueError("Incomplete escape sequence")
                    break

                if escape:
                    if hex_mode:
                        if char.lower() in "0123456789abcdef":
                            hex_buffer += char
                            if len(hex_buffer) == 2:
                                text += bytes.fromhex(hex_buffer).decode("latin-1")
                                hex_mode = False
                                escape = False
                        else:
                            raise ValueError("Invalid hexadecimal escape sequence")
                    elif control == "" and char == "'":
                        hex_mode = True
                        hex_buffer = ""
                    elif control == "" and char == "~":
                        text += "\u00a0"
                        escape = False
                    elif char.isalpha() and param == "":
                        control += char
                    elif char.isdigit() or (char == "-" and param == ""):
                        param += char
                    else:
                        if control in {"par", "line"}:
                            text += "\n"
                        elif control == "tab":
                            text += "\t"
                        elif control == "emdash":
                            text += "—"
                        elif control == "endash":
                            text += "–"
                        elif control == "u" and param:
                            codepoint = int(param)
                            if codepoint < 0:  # pragma: no cover
                                codepoint += 65536
                            text += chr(codepoint)
                            if char == "'":  # pragma: no cover
                                fallback = file.read(2)
                                if len(fallback) < 2 or any(
                                    c.lower() not in "0123456789abcdef"
                                    for c in fallback
                                ):  # pragma: no cover
                                    raise ValueError(
                                        "Invalid unicode fallback",
                                    )  # pragma: no cover
                            elif char == "\\":
                                next_char = file.read(1)
                                if next_char != "'":  # pragma: no cover
                                    raise ValueError(
                                        "Invalid unicode fallback",
                                    )  # pragma: no cover
                                fallback = file.read(2)
                                if len(fallback) < 2 or any(
                                    c.lower() not in "0123456789abcdef"
                                    for c in fallback
                                ):  # pragma: no cover
                                    raise ValueError(
                                        "Invalid unicode fallback",
                                    )  # pragma: no cover
                            elif char not in {" ", "\n"}:  # pragma: no cover
                                pass
                            control = ""
                            param = ""
                            escape = False
                            continue
                        elif control == "" and char == "\n":
                            text += "\n"
                        elif control == "" and char != "\\":
                            text += char
                        control = ""
                        param = ""
                        if char == "\\":
                            escape = True
                            hex_mode = False
                            continue
                        escape = False
                    continue

                if char == "{":
                    brace_depth += 1
                    continue
                if char == "}":
                    brace_depth -= 1
                    if brace_depth < 0:
                        raise ValueError("Unmatched closing brace")
                    continue

                if ignoring_header:
                    if char == "\n":
                        if last_char_was_newline:
                            ignoring_header = False
                        last_char_was_newline = True
                    else:
                        last_char_was_newline = False
                    continue

                if char == "\\":
                    escape = True
                    control = ""
                    param = ""
                    hex_mode = False
                    continue

                text += char

        if brace_depth != 0:
            raise ValueError("Unmatched opening brace")
        return text

    def __init__(self, file_name: str) -> None:
        self.file_name: str = file_name
        self.__cached_plain_text: Optional[str] = None
        self.__last_cache_update_time: Optional[str] = None

    def plain_text(self) -> str:
        last_update_time: str = self.last_update_time()
        # Refresh the cache when the source file has been updated or when
        # plain text has not yet been generated. Relying on an ``assert`` to
        # guarantee the cache exists could lead to returning ``None`` when
        # Python is run with optimization flags that skip assertions. Instead
        # perform an explicit check and lazily populate the cache as needed.
        if (
            self.__cached_plain_text is None
            or self.__last_cache_update_time is None
            or self.__last_cache_update_time != last_update_time
        ):
            self.__cached_plain_text = self.to_plain_text(self.file_name)
            self.__last_cache_update_time = last_update_time
        return self.__cached_plain_text

    def last_update_time(self) -> str:
        return time.ctime(os.path.getmtime(self.file_name))

    def dump(self, file_name: str) -> bool:
        try:
            with open(file_name, "w", encoding="latin-1") as file:
                file.write(self.plain_text())
            return True
        except OSError:
            return False


def main() -> None:
    if len(sys.argv) == 2:
        print(RTF(sys.argv[1]).plain_text())
    elif len(sys.argv) == 3:
        RTF(sys.argv[1]).dump(sys.argv[2])
    else:
        print(f"Usage: {sys.argv[0]} <input_file> [output_file]")


if __name__ == "__main__":
    main()  # pragma: no cover
