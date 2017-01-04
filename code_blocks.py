#!/usr/bin/env python

r"""Code Blocks, a program and library for drawing presentable VentureScript code blocks.

Features
--------

- Processes executable .vnts sources with lightweight annotations
- Syntax highlighting
- Line numbering
- Coloring model, observation, inference, and query code
- Emits embedable .pdf or .png graphics for iterating with
  collaborators, or \input-able .tex source for inclusion in
  publications.

How to use
----------

1. Annotate your program with comments indicating which part you wish
   to display as what.

2. Run `code_blocks.py <source files>` (in order) to generate a .png,
   .pdf, or .tex file.  See code_blocks.py -h for invocation details.

Dependencies
------------

Code Blocks requires Python 2.7.

If you want to generate .png output, you will need ImageMagick,
specifically the `convert` program.  On Ubuntu, do
  sudo apt-get install imagemagick

You will also of course need LaTeX for Code Blocks to be useful (but
you _can_ run it to produce .tex input files even without LaTeX being
installed).

Annotation format
-----------------

Code Blocks will look in your source file(s) for VentureScript
comments in this syntax:
  // -*- model
  assume ...
  // -*- hide

That means all the statements after the `-*- model` comment but before
the `-*- hide` comment are a "model" block, which should be emitted
and colorized as such.

The following block types are supported:
  // -*- model
  // -*- observation
  // -*- inference
  // -*- query
  // -*- hide

The first four are treated the same, except for the background color
they get; the `-*- hide` comment tells Code Blocks not to display
subsequent lines (until the next non-hide comment).

You may optionally write a number after your comment, like this:
  // -*- model -2
  assume ...

The number tells Code Blocks to indent (outdent, if negative) the
following lines that many additional spaces.  This may be helpful for
showing a code snippet that is indented for some reason (e.g., is
inside a function definition) as though it were not indented.

How to use the \input-able .tex
-------------------------------

Code Blocks can generate .tex input for use in a larger publication.
This will come in the form of a file containing several
`\begin{lstlisting}...\end{lstlisting}` environments with appropriate
content and options.  To use these, take care to

1. Use the color and listings packages
  \usepackage{color}
  \usepackage{listings}

2. Include the output of Code Blocks in the desired tex document with
  `\input{filename}`

3. Provide definitions for the elements that the generated snippets
   will require:
   - The VentureScript lstlistings language, which defines the desired
     syntax highlighting
     - This must include the option `escapeinside={(*@}{@*)}`
   - The commands `\hashtag` and `\hashsep` (for syntax highlighting
     of `#` and `:` in VentureScript code)
   - The colors modelblock, observationblock, inferenceblock, and
     queryblock, which are the background colors of those blocks.
   For an example, see the tex_header.tex template file that ships with
   Code Blocks.

"""

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
        self._mode = 'hide'
        self.indent = 0

    def consume_line(self, line):
        m = re.match(r'^\s*//\s*-[*]-\s*(hide|model|observation|inference|query)\s*([0-9-]*)?', line)
        if m:
            self.set_mode(m.group(1))
            if m.group(2) == '':
                self.indent = 0
            else:
                self.indent = int(m.group(2))
        else:
            if self._mode != 'hide':
                self._start_block_if_needed()
                self.blocks[-1].add_line(self._do_indent(line))

    def _do_indent(self, line):
        if re.match(r'^\s*$', line):
            # Do not in- or out-dent blank lines
            return line
        if self.indent >= 0:
            return (' ' * self.indent) + line
        else:
            outdent = -self.indent
            assert line[:outdent] == ' ' * outdent
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
    line = re.sub(r'#(.*):', r'(*@\hashtag @*)\1(*@\hashsep @*)', line)
    line = re.sub(r'#', r'(*@\hashtag @*)', line)
    return line

def print_latex(result, stream=sys.stdout):
    for block in result.blocks:
        print >>stream, r'\begin{lstlisting}[language=VentureScript,frame=single,backgroundcolor=\color{' + block.mode + 'block}]'
        for line in block.lines:
            stream.write(colorize_hash_tags(line))
        print >>stream, r'\end{lstlisting}'

def embeddable_tex_file(result, basename):
    filename = basename + '.tex'
    with open(filename, 'w') as f:
        print_latex(result, f)

def standalone_tex_file(result, basename):
    filename = basename + '.tex'
    shutil.copy(os.path.join(self_dir, 'tex_header.tex'), filename)
    with open(filename, 'a') as f:
        print_latex(result, f)
        print >>f, r'\end{document}'

def parser():
    p = argparse.ArgumentParser(description='Code Blocks, a program for drawing presentable VentureScript code blocks.',
                                epilog='See the module docstring for more information.')
    p.add_argument('file', nargs='+', help='Input file')
    p.add_argument('-o', '--output', default='code', help='Output file name.  Format deduced from extension')
    p.add_argument('-s', '--standalone', action='store_true', help='Produce standalone (not inputtable) tex output')
    return p

def write_output(result, target, standalone):
    path = os.path.dirname(target)
    os.chdir(path)
    filename = os.path.basename(target)
    (base, ext) = os.path.splitext(filename)
    if ext not in ['.png', '.pdf', '.tex']:
        print 'Only .png, .pdf, or .tex output formats supported, not', ext
        sys.exit(1)
    if ext in ['.png', '.pdf']:
        standalone_tex_file(result, base)
        subprocess.call(['pdflatex', base + '.tex'])
        subprocess.call(['convert', '-density', '400', base + '.pdf',
                         '-quality', '100', '-channel', 'RGBA', '-fill', 'white', '-opaque', 'none',
                         base + '.png'])
    elif standalone:
        standalone_tex_file(result, base)
        print 'Standalone tex file written to', target
    else:
        embeddable_tex_file(result, base)
        print 'Embeddable tex file written to', target

def main():
    p = parser()
    args = p.parse_args()
    target = os.path.realpath(args.output)
    result = parse_to_blocks(args.file)
    write_output(result, target, args.standalone)

if __name__ == '__main__':
    main()
