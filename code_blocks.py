#!/usr/bin/env python

import argparse
import os
import re
import shutil
import subprocess
import sys

self_dir = os.path.dirname(os.path.realpath(__file__))

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
        if re.match(r"^\s*$", line):
            # Do not in- or out-dent blank lines
            return line
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

def print_latex(result, stream=sys.stdout):
    for block in result.blocks:
        print >>stream, r"\begin{lstlisting}[language=VentureScript,frame=single]"
        for line in block.lines:
            stream.write(colorize_hash_tags(line))
        print >>stream, r"\end{lstlisting}"

def standalone_tex_file(result, basename):
    filename = basename + ".tex"
    shutil.copy(os.path.join(self_dir, "tex_header.tex"), filename)
    with open(filename, 'a') as f:
        print_latex(result, f)
        print >>f, r"\end{document}"

def parser():
    p = argparse.ArgumentParser(description='Code Blocks, a frob!')
    p.add_argument('--version', action='version', version='Code Blocks, version 0.1')
    p.add_argument('file', nargs="+", help='Input file')
    p.add_argument('-o', '--output', default="code", help="Output file name")
    return p

def write_output(result, target):
    path = os.path.dirname(target)
    os.chdir(path)
    filename = os.path.basename(target)
    (base, _ext) = os.path.splitext(filename)
    standalone_tex_file(result, base)
    subprocess.call(["pdflatex", base + ".tex"])
    subprocess.call(["convert", "-density", "400", base + ".pdf",
                     "-quality", "100", "-channel", "RGBA", "-fill", "white", "-opaque", "none",
                     base + ".png"])

def main():
    p = parser()
    args = p.parse_args()
    target = os.path.realpath(args.output)
    result = parse_to_blocks(args.file)
    write_output(result, target)

if __name__ == '__main__':
    main()
