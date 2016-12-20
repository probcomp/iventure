#!/usr/bin/env python

import re
import sys

class Block(object):
    def __init__(self, mode):
        self.mode = mode
        self.lines = []

    def add_line(self, line):
        self.lines.append(line)

class ResultBuilder(object):
    """Accumulate a parsing result from incoming pieces."""
    def __init__(self):
        self.blocks = []
        self._mode = "hide"
        self.indent = 0

    def consume_line(self, line):
        m = re.match(r"^\s*//\s*-[*]-\s*(hide|model|observation|inference|query)\s*([0-9-]*)?", line)
        if m:
            self.set_mode(m.group(1))
            if m.group(2) == '':
                self.indent = 0
            else:
                self.indent = int(m.group(2))
        else:
            if self._mode != "hide":
                self._start_block_if_needed()
                self.blocks[-1].add_line(self._do_indent(line))

    def _do_indent(self, line):
        if self.indent >= 0:
            return (" " * self.indent) + line
        else:
            outdent = -self.indent
            assert line[:outdent] == " " * outdent
            return line[outdent:]

    def set_mode(self, mode):
        self._mode = mode

    def _start_block_if_needed(self):
        if len(self.blocks) == 0:
            self.blocks.append(Block(self._mode))
        elif self.blocks[-1].mode != self._mode:
            self.blocks.append(Block(self._mode))
        else:
            pass

def parse_to_blocks(items):
    ans = ResultBuilder()
    for filename in items:
        with open(filename, 'r') as f:
            for line in f.readlines():
                ans.consume_line(line)
    return ans

def colorize_hash_tags(line):
    line = re.sub(r"#(.*):", r"(*@\hashtag @*)\1(*@\hashsep @*)", line)
    line = re.sub(r"#", r"(*@\hashtag @*)", line)
    return line

def print_latex(result):
    for block in result.blocks:
        print r"\begin{lstlisting}[language=VentureScript,frame=single]"
        for line in block.lines:
            sys.stdout.write(colorize_hash_tags(line))
        print r"\end{lstlisting}"

def main():
    print_latex(parse_to_blocks(sys.argv[1:]))

if __name__ == '__main__':
    main()
