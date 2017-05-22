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


function heatmap(df, labels) {
  var myCell = element.is('.output_subarea') ? element : element.next();
  if (typeof VizGPMReady === 'undefined') {
    throw new Error('VizGPM Display Library not loaded')
  }

  if (df.columns.length !== 3) {
    throw new Error('Must be 3 columns of data');
  }

  const toggleClass = (element, className, state) => {
    element.classList[state ? 'add' : 'remove'](className)
  }

  // convert the data to an MI object for VizGPM
  var associations = {}
  const columns = new Set();
  for (const [col0, col1, value] of df.data) {
    columns.add(col0);
    columns.add(col1);
    if (!associations[col0]) {
      associations[col0] = {}
    }
    associations[col0][col1] = value
  }

  function between(col1, col2) {
    return associations[col1][col2]
  }

  // This is what VizGPM expects for the mutual info charts
  var mi = { target: labels || [...columns], between: between }

  var container = $('<div style="display: flex; flex-direction: row;">')
    .appendTo(myCell);

  var depProbContainer = $('<div style="flex: 1 1 100%;">').appendTo(container);
  var columnListContainer = $('<div style="flex: 0 0 200px;">').appendTo(container);

  $("<style>.vizgpm-column-list .selected-columns-list .details{display: none !important;}</style>").appendTo(container);

  VizGPMReady.then(function(VizGPM) {
    const _ = VizGPM._;

    const SP = VizGPM.StateProperty

    const schema = [...columns].map(name => ({name}));

    var stateManager = new VizGPM.StateManager({
      [SP.SCHEMA]: {columns: schema},
      columns: [...columns],
      [SP.SELECTED_COLUMN_NAMES]: [],
      [SP.GET_COLUMN_FUNCTION]: col =>
        VizGPM.GpmHandler.prototype._getColumn.call(stateManager, col),
    });

    // var debug = $('<pre>').appendTo(element);
    // stateManager.subscribe(function(newState) {
    //   const showState = Object.assign({}, newState.state);
    //   delete showState.schema;
    //   delete showState.rows;
    //   debug.text(JSON.stringify(showState, false, '  '))
    // })

    const chart = new VizGPM.ZoomableColumnAssociation({
      root: depProbContainer[0],
      stateManager: stateManager,
      // subgridClass: SingleSelectSubgrid,
      associationFn: function() {
        return mi
      },
      // subgridConfig: {
        // cellSelectedFn: ({ xColumn, yColumn, selectedColumns: [x, y = x] = [] }) =>
          // xColumn === x && yColumn === y,
      // },
      // miniMapConfig: {
        // cellSelectedFn: ({ xColumn, yColumn, selectedColumns: [x, y = x] = [] }) =>
          // xColumn === x || yColumn === y,
      // },
    })

    const columnList = new VizGPM.UI.ColumnList({
      root: columnListContainer[0],
      stateManager,
    })
  })
}
