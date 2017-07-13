#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Copyright (c) 2010-2016, MIT Probabilistic Computing Project
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

r"""Code Blocks, drawing presentable VentureScript code blocks.

Features
--------

- Processes executable .vnts sources with lightweight annotations
- Syntax highlighting
- Line numbering
- Coloring model, observation, inference, and query code
- Optional manual highlights to code points of interest
- Controllable document width
- Emits embeddable .pdf or .png graphics for iterating with
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

You may highlight code snippets by surrounding them in special inline
comments, namely /*{*/ some important code here /*}*/.  This is
useful, for example, for showing differences from a previous code
figure.

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
     - This must include a definition of /| and |/ as delimiters, such
       as `moredelim=**[is][keywordstyle4]{/|}{|/}` (for syntax
       highlighting of `#` and `:` in VentureScript code)
     - If you use inline comments to highlight, this must also include
       a definition of /*{*/ and /*}*/ as delimiters that implements the
       desired highlighting effect.  See tex_header.tex for how
       this is done for the standalone output.
   - The colors modelblock, observationblock, inferenceblock, and
     queryblock, which are the background colors of those blocks.
   For an example, see the tex_header.tex template file that ships with
   Code Blocks.

Outstanding TODOs
-----------------

- [ ] Port to OSX (Should be straightforward, but Axch has no Mac)
- [ ] (Easy) Check whether `convert` is missing and give a nice
  error message; generate pdf output anyway.
- [ ] (Easy) Check whether `pdflatex` is missing and give a nice
  error message; generate tex output anyway.
- [ ] Accept input from .ipynb files (just need to deal with their
  quote marks and such).
- [ ] Tweak the default style to Vikash's taste (he specifically
  suggested bold-facing the keywords `assume` and co) (this should
  just be a matter of fiddling with the `tex_header.tex` file).
- [x] Continue the line numbers from one code block to the next
  in the same output.

Possible Additional Feaures / Use Cases
---------------------------------------

- Highlighting and uploading without leaving IPython.  Presumably this
  feature would requires the user to add some boilerplate to their
  IPython notebooks.  Should this be done based on this code base or
  some other way?  For example, by teaching Prism
  (http://prismjs.com/) to handle VS in IPython cells?

- Gross presentation control.  Maybe add some way to control some
  aspects of the graphical outputs, to allow better iteration before
  embedding into LaTeX.  I am specifically thinking of
  - Font
  - Font size
  - Whether line numbers continue or restart
  Does this want to be a few command line options spliced into the
  tex header (which now becomes a template)?  Ability to replace the
  template entirely?

- Zero-annotation input.  It may be nice to be able to make images of
  snippets without having to modify the input source files.  Axch was
  envisioning a command-line spec language, similar to pdfjam;
  something like this:
    code_blocks.py --model foo.vnts:3-14 --observation foo.vnts:15-17
      --inference bar.vnts
  which would make snippets of the given types out of the given line
  ranges of the given files.

- Alternate offline highlighter(s).  The VentureScript->png use case
  does not strictly need to use LaTeX as the syntax highlighter.
  Perhaps add others?

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

annot=r'^\s*//\s*-[*]-\s*([0-9a-zA-Z_-]+\s+)?(hide|model|observation|inference|query)\s*([0-9-]*)?'

class ResultBuilder(object):
    """Accumulate a parsing result from incoming pieces."""
    def __init__(self, name):
        self.name = name
        self.blocks = []
        self._mode = 'hide'
        self.indent = 0

    def _name_match(self, m):
        if self.name is None:
            return True
        if m.group(1) is None:
            return False
        return self.name == m.group(1).strip()

    def consume_line(self, line):
        m = re.match(annot, line)
        if m:
            if self._name_match(m):
                self.set_mode(m.group(2))
                if m.group(3) == '':
                    self.indent = 0
                else:
                    self.indent = int(m.group(3))
            else:
                self.set_mode('hide')
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
        if mode != 'hide':
            self._start_block_if_needed()

    def _start_block_if_needed(self):
        if len(self.blocks) == 0:
            self.blocks.append(Block(self._mode))
        elif self.blocks[-1].mode != self._mode:
            self.blocks.append(Block(self._mode))
        else:
            pass

    def num_selected_lines(self):
        return sum(len(b.lines) for b in self.blocks)

def parse_to_blocks(items, name):
    ans = ResultBuilder(name)
    for filename in items:
        with open(filename, 'r') as f:
            for line in f.readlines():
                ans.consume_line(line)
    return ans

def colorize_hash_tags(line):
    line = re.sub(r'#(.*):', r'/|#|/\1/|:|/', line)
    line = re.sub(r'#([^|])', r'/|#|/\1', line)
    return line

def print_latex(result, stream, args):
    for block in result.blocks:
        if len(block.lines) == 0: continue
        print >>stream, r'\lstset{firstnumber=last}'
        stream.write(r'\begin{lstlisting}[language=VentureScript,')
        stream.write(r'frame=single,')
        if not args.no_color:
            stream.write(r'backgroundcolor=\color{' + block.mode + 'block}')
        print >>stream, ']'
        for line in block.lines:
            stream.write(colorize_hash_tags(line))
        print >>stream, r'\end{lstlisting}'

def embeddable_tex_file(result, basename, args):
    filename = basename + '.tex'
    with open(filename, 'w') as f:
        print_latex(result, f, args)

def standalone_tex_file(result, basename, args):
    filename = basename + '.tex'
    shutil.copy(os.path.join(self_dir, 'tex_header.tex'), filename)
    with open(filename, 'a') as f:
        if args.width is not None:
            f.write(r'\setlength{\textwidth}{' + args.width + '}\n')
        f.write(r'''\begin{document}
\thispagestyle{plain}''')
        print_latex(result, f, args)
        print >>f, r'\end{document}'

def parser():
    p = argparse.ArgumentParser(
        description='Code Blocks, a program for drawing presentable ' \
            + 'VentureScript code blocks.',
        epilog='See the module docstring for more information.')
    p.add_argument('file', nargs='+', help='Input file')
    p.add_argument('-o', '--output', default='code.png',
        help='Output file name.  Format deduced from extension')
    p.add_argument('-s', '--standalone', action='store_true',
        help='Produce standalone (not inputtable) tex output')
    p.add_argument('-w', '--width',
        help='Tex distance to use as text width, e.g. 0.5\\textwidth for half')
    p.add_argument('--no-color', action='store_true',
        help='Suppress coloring code blocks by type.')
    p.add_argument('--name', help='Include only blocks with the given name.')
    return p

def write_output(result, target, args):
    path = os.path.dirname(target)
    os.chdir(path)
    filename = os.path.basename(target)
    (base, ext) = os.path.splitext(filename)
    if ext not in ['.png', '.pdf', '.tex']:
        print 'Only .png, .pdf, or .tex output formats supported, not', ext
        sys.exit(1)
    if ext in ['.png', '.pdf']:
        standalone_tex_file(result, base, args)
        subprocess.call(['pdflatex', base + '.tex'])
        subprocess.call(['convert', '-density', '400', base + '.pdf',
            '-quality', '100', '-channel', 'RGBA', '-fill', 'white',
            '-opaque', 'none', base + '.png'])
        print 'Image written to', base + '.png'
    elif args.standalone:
        standalone_tex_file(result, base, args)
        print 'Standalone tex file written to', target
    else:
        embeddable_tex_file(result, base, args)
        print 'Embeddable tex file written to', target
    print 'Rendered', result.num_selected_lines(), 'lines.'
    if result.num_selected_lines() == 0:
        print 'Did you remember to add a `// -*- model` or such comment to the input?'

def main():
    p = parser()
    args = p.parse_args()
    target = os.path.realpath(args.output)
    result = parse_to_blocks(args.file, args.name)
    write_output(result, target, args)

if __name__ == '__main__':
    main()
