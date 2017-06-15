# Converting iventure notebooks to pdf via LaTeX

This document outlines some steps for improving conversion of iventure Jupyter
notebooks to pdf via LaTeX. In particular, these steps:
- make pandas dataframes render as LaTeX tables when converted to pdf
- remove the `In[]:`and `Out[]:` before cells in the pdf
- remove all outputs that are just empty dataframes
- wrap text at the margin

## 1. Displaying pandas dataframes as LaTeX tables
Insert the following code into a code cell in the notebook and run it before
running any cells that output pandas dataframes. This will cause the dataframes
to render as they normally would in the HTML version of the notebook, but as
LaTeX tables in the pdf.

	import pandas as pd

	pd.set_option('display.notebook_repr_html', True)

	def _repr_latex_(self):
    	return self.to_latex()

	pd.DataFrame._repr_latex_ = _repr_latex_

## 2. Adding a custom template for LaTeX conversion
Add the following custom template as `custom.tplx` in `python2.7/site-packages/nbconvert/templates/latex/`
(may be overwritten during upgrades) or another directory of your choice. This
template wraps text at the margin, removes `In[]:` and `Out[]:` before cells in
the pdf, and removes all outputs that are just empty dataframes.

	((*- extends 'article.tplx' -*))
	%===============================================================================
	% Input
	%===============================================================================
	((* block input scoped *))
	   ((( custom_add_prompt(cell.source | wrap_text(88) | highlight_code(strip_verbatim=True), cell) )))
	((* endblock input *))
	%===============================================================================
	% Output
	%===============================================================================
	((* block execute_result scoped *))
	    ((*- for type in output.data | filter_data_type -*))
	        ((*- if type in ['text/plain']*))
	            ((*- if "Empty DataFrame" in output.data['text/plain']*))
	                ((( custom_add_prompt('' | wrap_text(88) |  escape_latex, cell) )))
	            ((* else -*))
	                ((( custom_add_prompt(output.data['text/plain'] | wrap_text(88) |  escape_latex, cell) )))
	            ((*- endif -*))
	        ((* else -*))
	            ((( super() )))
	        ((*- endif -*))
	    ((*- endfor -*))
	((* endblock execute_result *))
	%==============================================================================
	% Define macro custom_add_prompt() (derived from add_prompt() macro in style_ipython.tplx)
	%==============================================================================
	((* macro custom_add_prompt(text, cell) -*))
	\begin{Verbatim}[commandchars=\\\{\},fontsize=\scriptsize]
	((( text )))
	\end{Verbatim}
	((*- endmacro *))

## 3. Adding a custom style_ipython template
Replace the existing `python2.7/site-packages/nbconvert/templates/latex/style_ipython.tplx`
with the following. NOTE: this file may be overwritten by upgrades, so it is also
possible to put this file in a another directory (as long as the
`style_ipython.tplx` in `python2.7/site-packages/nbconvert/templates/latex/` is
renamed to avoid conflicts). There is a one-line change in
`((* block execute_result scoped *))`, which completes the removal of `In[]:`
and `Out[]:` when `super()` is called from a subclass.

	((= IPython input/output style =))
	((*- extends 'base.tplx' -*))
	% Custom definitions
	((* block definitions *))
	    ((( super() )))
	    % Pygments definitions
	    ((( resources.latex.pygments_definitions )))
	    % Exact colors from NB
	    \definecolor{incolor}{rgb}{0.0, 0.0, 0.5}
	    \definecolor{outcolor}{rgb}{0.545, 0.0, 0.0}
	((* endblock definitions *))
	%===============================================================================
	% Input
	%===============================================================================
	((* block input scoped *))
	    ((( add_prompt(cell.source | highlight_code(strip_verbatim=True), cell, 'In', 'incolor') )))
	((* endblock input *))
	%===============================================================================
	% Output
	%===============================================================================
	((* block execute_result scoped *))
	    ((*- for type in output.data | filter_data_type -*))
	        ((*- if type in ['text/plain']*))
	            ((( add_prompt(output.data['text/plain'] | escape_latex, cell, 'Out', 'outcolor') )))
	        ((* else -*))
	            ((( super() )))
	        ((*- endif -*))
	    ((*- endfor -*))
	((* endblock execute_result *))
	%==============================================================================
	% Support Macros
	%==============================================================================
	% Name: draw_prompt
	% Purpose: Renders an output/input prompt
	((* macro add_prompt(text, cell, prompt, prompt_color) -*))
	    ((*- if cell.execution_count is defined -*))
	    ((*- set execution_count = "" ~ (cell.execution_count | replace(None, " ")) -*))
	    ((*- else -*))
	    ((*- set execution_count = " " -*))
	    ((*- endif -*))
	    ((*- set indention =  " " * (execution_count | length + 7) -*))
	\begin{Verbatim}[commandchars=\\\{\}]
	((( text | add_prompts(first='{\color{' ~ prompt_color ~ '}' ~ prompt ~ '[{\\color{' ~ prompt_color ~ '}' ~ execution_count ~ '}]:} ', cont=indention) )))
	\end{Verbatim}
	((*- endmacro *))

## 4. Running nbconvert
From the directory of the desired Jupyter notebook, you can now run:
`jupyter nbconvert --to pdf --template /path/to/custom.tplx <notebook name>`.
Note that being able to specify absolute paths to template files may require
upgrading `nbconvert`.