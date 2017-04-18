//   Copyright (c) 2010-2016, MIT Probabilistic Computing Project
//
//   Licensed under the Apache License, Version 2.0 (the "License");
//   you may not use this file except in compliance with the License.
//   You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
//   Unless required by applicable law or agreed to in writing, software
//   distributed under the License is distributed on an "AS IS" BASIS,
//   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//   See the License for the specific language governing permissions and
//   limitations under the License.

function depprob_demo(depprob, rows, schema) {
  var myCell = element.is('.output_subarea') ? element : element.next();
  if (typeof VizGPMReady === 'undefined') {
    throw new Error('VizGPM Display Library not loaded')
  }

  // double check that it looks like the data frame we want
  if (!(depprob.name0 && depprob.name1 && depprob.value)) {
    throw new Error('Unknown depprob data format, expected { name0: [], name1: [], value: [] }')
  }

  const toggleClass = (element, className, state) => {
    element.classList[state ? 'add' : 'remove'](className)
  }


  if (schema) {
    for (const col of schema) {
      if (col.stat_type == 'numerical') {
        col.stat_type = 'realAdditive';
      }

      if (col.stat_type == 'nominal') {
        col.stat_type = 'categorical';
      }
    }
  }

  // convert the data to an MI object for VizGPM
  var associations = {}
  // very strangely, the pandas data frame json looks like an object
  // with indexes and has no "length" propery
  for (var index in depprob.name0) {
    if (!associations[depprob.name0[index]]) {
      associations[depprob.name0[index]] = {}
    }
    associations[depprob.name0[index]][depprob.name1[index]] =
      depprob.value[index]
  }

  function between(col1, col2) {
    return associations[col1][col2]
  }

  var columns = Object.keys(associations)
  // This is what VizGPM expects for the mutual info charts
  var mi = { target: columns, between: between }

  var container = $('<div style="display: flex; flex-direction: row;">')
    .appendTo(myCell);

  var depProbContainer = $('<div style="flex: 1 1 100%;">').appendTo(container);
  var pairContainer = $('<div style="flex: 0 0 225px;">').appendTo(container);

  VizGPMReady.then(function(VizGPM) {
    const _ = VizGPM._;

    const SP = VizGPM.StateProperty

    var clustered = VizGPM.util.treecluster(mi)
    mi.target = clustered
    // The GPMStateManager actually assumes a JS remoteGPM, so we should
    // create our own stateManager with a `getColumn` method

    var stateManager = new VizGPM.StateManager({
      [SP.SCHEMA]: {columns: schema},
      [SP.SELECTED_COLUMN_NAMES]: [],
      [SP.GET_COLUMN_FUNCTION]: col =>
        VizGPM.GpmHandler.prototype._getColumn.call(stateManager, col),
      [SP.DISPLAYED_ROWS]: rows,
    });

    // var debug = $('<pre>').appendTo(element);
    // stateManager.subscribe(function(newState) {
    //   const showState = Object.assign({}, newState.state);
    //   delete showState.schema;
    //   delete showState.rows;
    //   debug.text(JSON.stringify(showState, false, '  '))
    // })

    class SingleSelectSubgrid extends VizGPM.Charts.ColumnAssociationSubgrid {
      // I used to have these sorts of events as parameters to the constructor,
      // this is a private API but the only way I can handle making a "single
      // select subgrid"
      _handleGridMouseDown(event) {
        return this._handleAllMouseEvents(event)
      }

      _handleGridMouseUp() {
        // Doesn't actually get the event?  It's okay - we don't want to do anything anyway
        return
      }

      _handleGridMouseMove(event) {
        return this._handleAllMouseEvents(event)
      }

      _handleAllMouseEvents(event) {
        const { x, y, error } = this._gridEventCoords(event) || { error: true };
        if (!error && event.which) {
          // if there was a button pressed, we want to set selected columns
          const selectedColumns = [...new Set([
              this._columnNameAtXIndex(x), this._columnNameAtYIndex(y)
            ])]

          // TODO: Don't thrash state so much when they are deep equal
          this.setState({[SP.FOCUSED_COLUMN_NAMES]: selectedColumns})
          this.setState({[SP.SELECTED_COLUMN_NAMES]: selectedColumns})
        } else if (event.type === 'mousemove') {
          // Otherwise, we want to still handle focused columns as we used to
          super._handleGridMouseMove(event)
        }
      }

      _handleXLabelClick(xIndex) {
        this.setState({[SP.SELECTED_COLUMN_NAMES]: [this._columnNameAtXIndex(xIndex)]});
      }

      _handleYLabelClick(yIndex) {
        this.setState({[SP.SELECTED_COLUMN_NAMES]: [this._columnNameAtXIndex(yIndex)]});
      }

      // customize the painting of selection to be [x, y] like focus is.
      _updateSelectedAndFocusedColumns(state) {
        const {
          [SP.SELECTED_COLUMN_NAMES]: selected = [],
          [SP.FOCUSED_COLUMN_NAMES]: focused = [],
        } = state

        for (const cell of this._grid.querySelectorAll('.grid-cell.focused,.grid-cell.selected')) {
          cell.classList.remove('focused');
          cell.classList.remove('selected');
        }

        // Make [x] into [x, x]
        const [selX, selY = selX] = selected;
        const [focX, focY = focX] = focused;
        const indexer = {}
        this._columnXLabels.forEach((label, index) => {
          const name = this._columnNameAtXIndex(index)
          if (selX === name) {
            label.classList.add('selected')
            indexer.selX = index;
          } else {
            label.classList.remove('selected')
          }

          if (focX === name) {
            label.classList.add('focused')
            indexer.focX = index;
          } else {
            label.classList.remove('focused')
          }
        })

        this._columnYLabels.forEach((label, index) => {
          const name = this._columnNameAtYIndex(index)
          if (selY === name) {
            label.classList.add('selected')
            indexer.selY = index;
          } else {
            label.classList.remove('selected')
          }

          if (focY === name) {
            label.classList.add('focused')
            indexer.focY = index;
          } else {
            label.classList.remove('focused')
          }
        })

        if ('selX' in indexer && 'selY' in indexer) {
          this._gridCells[indexer.selY][indexer.selX].classList.add('selected');
        }

        if ('focX' in indexer && 'focY' in indexer && !_.isEqual(selected, focused)) {
          this._gridCells[indexer.focY][indexer.focX].classList.add('focused');
        }
      }
    }

    const chart = new VizGPM.ZoomableColumnAssociation({
      root: depProbContainer[0],
      stateManager: stateManager,
      subgridClass: SingleSelectSubgrid,
      associationFn: function() {
        return mi
      },
      subgridConfig: {
        cellSelectedFn: ({ xColumn, yColumn, selectedColumns: [x, y = x] = [] }) =>
          xColumn === x && yColumn === y,
      },
      miniMapConfig: {
        cellSelectedFn: ({ xColumn, yColumn, selectedColumns: [x, y = x] = [] }) =>
          xColumn === x || yColumn === y,
      },
    })

    class SingleCellPairPlot extends VizGPM.PairPlot {
      _buildPairPlot() {
        const {registry, axisLabelFn, axisDescriptionFn} = this._;
        const state = this.getState();
        const rows = state[SP.DISPLAYED_ROWS] || [];
        const schema = state[SP.SCHEMA];
        const selectedColumns = state[SP.SELECTED_COLUMN_NAMES] || [];

        if (!(registry && schema &&
            selectedColumns[0] && rows[0] && selectedColumns[0] in rows[0])) {
          return document.createElement('div');
        }

        const [ rowName, colName = rowName ] = selectedColumns;
        // flip x,y so that the axis labels are correct
        const chart = this.getChartForIntersection(colName, rowName);
        this._charts.push(chart);

        return chart.getRoot();
      }
    }

    if (rows && schema) {
      const plot = new SingleCellPairPlot({
        root: pairContainer[0],
        stateManager: stateManager,
      })
    }
  })
}
