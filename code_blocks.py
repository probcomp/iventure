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

    def consume_line(self, line):
        m = re.match(r"^\s*//\s*-[*]-\s*(hide|model|observation|inference|query)", line)
        if m:
            self.set_mode(m.group(1))
        else:
            if self._mode != "hide":
                self._start_block_if_needed()
                self.blocks[-1].add_line(line)

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
