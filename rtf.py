#!/usr/bin/env python3
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
        """Return the plain text representation of ``file_name``.

        Parameters
        ----------
        file_name:
            Path to the RTF file.
        """

        text: str = ""
        ignoring_header: bool = True
        last_char_was_newline: bool = False
        ignoring_escaped_characters: bool = False
        escaped_characters: Optional[str] = None

        with open(file_name, encoding="latin-1") as file:
            while True:
                char: str = file.read(1)
                if not char:
                    break

                if char == "\\":
                    ignoring_escaped_characters = True

                if not ignoring_header:
                    if ignoring_escaped_characters:
                        if char == "\\":
                            escaped_characters = ""
                        elif char == " ":
                            ignoring_escaped_characters = False
                        elif char == "\n":
                            ignoring_escaped_characters = False
                            text += "\n"
                        else:
                            if escaped_characters is not None:
                                escaped_characters += char
                    elif char not in ("{", "}"):
                        text += char

                if char == "\n":
                    if last_char_was_newline:
                        ignoring_header = False
                        ignoring_escaped_characters = False
                    last_char_was_newline = True
                else:
                    last_char_was_newline = False

        return text

    def __init__(self, file_name: str) -> None:
        self.file_name: str = file_name
        self.__cached_plain_text: Optional[str] = None
        self.__last_cache_update_time: Optional[str] = None

    def plain_text(self) -> str:
        last_update_time: str = self.last_update_time()
        if (
            self.__last_cache_update_time is None
            or self.__last_cache_update_time != last_update_time
        ):
            self.__cached_plain_text = self.to_plain_text(self.file_name)
            self.__last_cache_update_time = last_update_time
        assert self.__cached_plain_text is not None
        return self.__cached_plain_text

    def last_update_time(self) -> str:
        return time.ctime(os.path.getmtime(self.file_name))

    def dump(self, file_name: str) -> bool:
        try:
            with open(file_name, "w+", encoding="latin-1") as file:
                file.write(self.plain_text())
            return True
        except OSError:
            return False


def main() -> None:
    if len(sys.argv) == 2:
        print(RTF(sys.argv[1]).plain_text())
    elif len(sys.argv) == 3:
        RTF(sys.argv[1]).dump(sys.argv[2])


if __name__ == "__main__":
    main()
