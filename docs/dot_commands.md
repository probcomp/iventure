# jupyter_probcomp dot commands
Dot commands in the BQL section below should be prepended by `%bql` (for
single-line commands) or `%%bql` (for multi-line commands). Similarly, those in
the MML section should be prepended by `%mml` or `%%mml` and those in the SQL
section should be prepended by `%sql` or `%%sql`.

## BQL
- `%bql .assert <query>`

	Returns a message indicating whether the test represented by `<query>`
	passed or failed, i.e. whether `<query>` returned 1 or 0.

- `%bql	.nullify <table> <value>`

	Converts all instances of `<value>` in `<table>` to SQL `NULL`.

- `%bql	.population <population>`

	Returns a table of the variables (including their statistical types) and
	generators for `<population>`.

- `%bql .subsample_columns <table> <subsampled_table> <limit> [--keep <col> [<col> ...]] [--seed SEED]`

	Creates a new table named `<subsampled_table>` containing `<limit>` columns
	from `<table>`. Any columns listed after the `--keep` flag are kept, columns
	listed after `--drop` flag are dropped, and the remainder are randomly
	sampled from `<table>`.

- `%bql	.table <table>`

	Returns a table of the PRAGMA schema of `<table>`.

### Plotting
#### Interactive
Interactive plotting can be enabled by running `%vizgpm inline`.
The following dot commands work the same as their standard equivalents below,
with additional capabilities for scrolling around and selecting data in the
plots.

- `%bql .interactive_bar <query>`

- `%bql .interactive_heatmap <query>`

- `%bql .interactive_scatter <query>`

Additionally, interactive plotting includes pairplots:

- `%bql .interactive_pairplot <query>`

	Pairplot of the data points in the table returned by `<query>`.

#### Standard
The following plotting dot commands can take several optional arguments,
described in "Optional arguments" below. Each dot command can take multiple
optional arguments in `[options]`, each of the form `--<arg>=<value>`.

- `%bql .bar [options] <query>`

	Vertical barplot of the data points in the table returned by `<query>`. The
	first column is (nominal) names, and the second column is (numerical)
	values.

- `%bql .barh [options] <query>`

	Horizontal barplot of the data points in the table returned by `<query>`.
	The first column is (nominal) names, and the second column is (numerical)
	values.

- `%bql .clustermap [options] <query>`

	Clustermap plotted by pivoting the last three columns of the table returned
	by `<query>` (typically an `ESTIMATE PAIRWISE` query in BQL).

- `%bql .density [options] <query>`

	Density plot of the data points in the table returned by `<query>`. If the
	table has one column, then a regular density plot is produced. If the table
	has two columns, then the final column is used as the label for each data
	point.

- `%bql .heatmap [options] <query>`

	Heatmap plotted by pivoting the last three columns of the table returned by
	`<query>` (typically an `ESTIMATE PAIRWISE` query in BQL).

- `%bql .histogram_nominal [options] <query>`

	Histogram of the NOMINAL data points in the table returned by `<query>`. If
	the table has one column, then a regular histogram is produced. If the table
	has two columns, then the final column is used as the label for each data
	point.

- `%bql .histogram_numerical [options] <query>`

	Histogram of the NUMERICAL data points in the table returned by `<query>`.
	If the table has one column, then a regular histogram is produced. If the
	table has two columns, then the final column is used as the label for each
	data point.

- `%bql .render_crosscat [special_options] <generator_name> <model_number>`

	Renders the state of the CrossCat model `<model_number>` in
	`<generator_name>`. Instead of the standard optional arguments, this
	function takes the following special optional arguments:
	- `--subsample=<n>`

		Number of rows to subsample (recommend <50).

    - `--width=<w>`

    	Width of the figure.

    - `--height=<c>`

    	Height of the figure.

    - `--rowlabels=<colname>`

    	Name of the column in the base table to use as row labels.

    - `--progress=[True|False]`

    	Whether to show a progress bar.

    - `--yticklabeslize=<fontsize>`

    	Size of the row labels.

    - `--xticklabeslize=<fontsize>`

    	Size of the column labels.

- `%bql .scatter [options] <query>`

	Scatter plot of the NUMERICAL data points in the table returned by
	`<query>`. If the table has two columns, then a regular scatter plot is
	produced. If the table has three columns, then the final column is used as
	the label for each data point.

##### Optional arguments
- `xmin=<value>`

	Sets the minimum x-axis value to `<value>`.

- `xmax=<value>`

	Sets the maximum x-axis value to `<value>`.

- `ymin=<value>`

	Sets the minimum y-axis value to `<value>`.

- `ymax=<value>`

	Sets the maximum y-axis value to `<value>`.

- `xlog=<base>`

	Sets the x scale to logarithmic with base `<base>`.

- `ylog=<base>`

	Sets the y scale to logarithmic with base `<base>`.

- `xlabel=<value>`

	Sets the x-axis label to `<value>`.

- `ylabel=<value>`

	Sets the y-axis label to `<value>`.

- `rug=[True|False]`

	For `.density` only. Default `True`. Setting to `False` turns off plotting
	rug marks (the tick marks on the x-axis indicating individual values).

- `shade=[True|False]`

	For `.density` only. Default `True`. Setting to `False` turns off shading
	the area under the density curve.

## MML
- `%mml .guess_schema <table>`

	Returns an MML schema using the guessed statistical types for the columns of
	`<table>`.

## SQL
- `%sql .regress_sql [--table=<table>] <query>`

	Returns a table of the results of a BQL REGRESS `<query>`.
