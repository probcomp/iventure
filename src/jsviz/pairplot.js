function pairplot(df, schema) {
  var myCell = element.is('.output_subarea') ? element : element.next();
  if (typeof VizGPMReady === 'undefined') {
    throw new Error('VizGPM Display Library not loaded')
  }

  var container = $('<div>')
    .appendTo(myCell);

  VizGPMReady.then(function(VizGPM) {
    const _ = VizGPM._;

    const SP = VizGPM.StateProperty

    for (const col of schema) {
      if (col.stat_type == 'numerical') {
        col.stat_type = 'realAdditive';
      }

      if (col.stat_type == 'nominal') {
        col.stat_type = 'categorical';
      }
    }

    function rowProxy(__key) {
      const obj = {__key};
      for (const column of df.columns) {
        obj[column] = df.data[__key].shift();
      }
      return obj;
    }

    const rows = [];
    for(let index = 0; index < df.data.length; index++) {
      rows.push(rowProxy(index));
    }

    var stateManager = new VizGPM.StateManager({
      [SP.SCHEMA]: {columns: schema},
      [SP.SELECTED_COLUMN_NAMES]: df.columns,
      [SP.GET_COLUMN_FUNCTION]: col =>
        VizGPM.GpmHandler.prototype._getColumn.call(stateManager, col),
      [SP.DATA_ROWS]: rows,
      [SP.DISPLAYED_ROWS]: rows,
    });

    // When the selection query changes, update the selected rows
    stateManager.subscribe(({ changed, state }) => {
      if (changed.indexOf(SP.SELECTION_QUERY) !== -1) {
        stateManager.set({
          [SP.DISPLAYED_SELECTION_QUERY]: state[SP.SELECTION_QUERY],
          [SP.SELECTED_ROWS]:
              VizGPM.GpmHandler.prototype._getSelectedRows(state, state[SP.SELECTION_QUERY]),
        });
      }
    });

    const plot = new VizGPM.PairPlot({
      root: container[0],
      stateManager: stateManager,
    });
  })
}
