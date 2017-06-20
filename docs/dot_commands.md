# iventure dot commands
Dot commands in the BQL section below should be prepended by `%bql` (for
single-line commands) or `%%bql` (for multi-line commands). Similarly, those in
the MML section should be prepended by `%mml` or `%%mml` and those in the SQL
section should be prepended by `%sql` or `%%sql`.

## BQL
- `%bql .assert <query>`

	Returns a message indicating whether the test represented by `<query>` passed or
	failed, i.e. whether `<query>` returned 1 or 0.

- `%bql	.nullify <table> <value>`

	Converts all instances of `<value>` in `<table>` to SQL `NULL`.

- `%bql	.population <population>`

	Returns a table of the variables (including their statistical types) and
	metamodels for `<population>`.

- `%bql .subsample_columns [--keep=col1,col2,col3...] <table> <subsampled_table> <limit>`

	Creates a new table named `<subsampled_table>` containing `<limit>` columns
	from `<table>`. Any columns listed after the `--keep` flag are kept, and the
	remainder are randomly sampled from `<table>`.

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
	first column is (nominal) names, and the second column is (numerical) values.

- `%bql .barh [options] <query>`

	Horizontal barplot of the data points in the table returned by `<query>`. The
	first column is (nominal) names, and the second column is (numerical) values.

- `%bql .clustermap [options] <query>`

	Clustermap plotted by pivoting the last three columns of the table returned by
	`<query>` (typically an `ESTIMATE PAIRWISE` query in BQL).

- `%bql .density [options] <query>`

	Density plot of the data points in the table returned by `<query>`. If the table
	has one column, then a regular density plot is produced. If the table has two
	columns, then the final column is used as the label for each data point.

- `%bql .heatmap [options] <query>`

	Heatmap plotted by pivoting the last three columns of the table returned by
	`<query>` (typically an `ESTIMATE PAIRWISE` query in BQL).

- `%bql .histogram_nominal [options] <query>`

	Histogram of the NOMINAL data points in the table returned by `<query>`. If the
	table has one column, then a regular histogram is produced. If the table has two
	columns, then the final column is used as the label for each data point.

- `%bql .histogram_numerical [options] <query>`

	Histogram of the NUMERICAL data points in the table returned by `<query>`. If
	the table has one column, then a regular histogram is produced. If the table has
	two columns, then the final column is used as the label for each data point.

- `%bql .scatter [options] <query>`

	Scatter plot of the NUMERICAL data points in the table returned by `<query>`. If
	the table has two columns, then a regular scatter plot is produced. If the table
	has three columns, then the final column is used as the label for each data
	point.

##### Optional arguments
- `xmin=<value>`

	Sets the minimum x-axis value to `<value>`.

- `xmax=<value>`

	Sets the maximum x-axis value to `<value>`.

- `ymin=<value>`

	Sets the minimum y-axis value to `<value>`.

- `ymax=<value>`

	Sets the maximum y-axis value to `<value>`.

- `xlog=<value>`

	If `<value>` is `True`, sets the x scale to logarithmic. If `<value>` is `False`,
	sets the x scale to linear.

- `ylog=<value>`

	If `<value>` is `True`, sets the y scale to logarithmic. If `<value>` is `False`,
	sets the y scale to linear.

- `xlabel=<value>`

	Sets the x-axis label to `<value>`.

- `ylabel=<value>`

	Sets the y-axis label to `<value>`.

- `rug=<value>`

	For `.density` only. Default `<value>` is `True`. Setting `<value>` to
	`False` turns off plotting rug marks (the tick marks on the x-axis
	indicating individual values).

- `shade=<value>`

	For `.density` only. Default `<value>` is `True`. Setting `<value>` to
	`False` turns off shading the area under the density curve.

## MML
- `%mml .guess_schema [--reasons] <table>`

	Returns an MML schema using the guessed statistical types for the columns of
	`<table>`. Using the `--reasons` flag includes the heuristic reasons for the
	statistical type guesses.

## SQL
- `%sql .regress_sql [--table=<table>] <query>`

	Returns a table of the results of a BQL REGRESS `<query>`.
