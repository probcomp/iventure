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

function scatter(df) {
  var myCell = element.is('.output_subarea') ? element : element.next();

  // Validate input format.  It should be a pandas dataframe in "split" format:
  // df.to_json(orient="split")

  if (!(df.columns && df.index && df.data)) {
    throw new Error("Incorrect data format");
  }

  if (df.columns.length < 2 || df.columns.length > 3) {
    debugger;
    throw new Error("There must be two or three columns");
  }

  if (!df.data.length) {
    throw new Error("No data in the table");
  }

  if (typeof df.data[0][1] !== 'number') {
    throw new Error("Expected second column to contain a number");
  }

  const [ xName, yName, colorName ] = df.columns;
  const container = $("<div>").css({ display: 'flex', flexDiection: 'row' }).appendTo(myCell.empty());


  function $s(elem) {
    return $(document.createElementNS('http://www.w3.org/2000/svg', elem));
  }
  const svg = $s('svg').attr({ width: 15, height: 500 })
    .append($s('text').attr({transform: "rotate(270) translate(-250 12)", size:"12", style: "fill: #000000", 'text-anchor': "middle", 'font-weight': 'bold'}).text(yName));

  $('<div style="flex: 0 0 15px">').append(svg).appendTo(container);

  const middleContainer = $('<div style="display: flex; flex-direction: column">').appendTo(container);
  middleContainer.append($('<div style="text-align: center; font-weight: bold">').text(xName));

  VizGPMReady
  .then(VizGPM => {
    const _ = VizGPM._;
    const root = $("<div>").css({ display: 'inline-block', width: 500, verticalAlign: 'top' }).prependTo(middleContainer)[0];

    const xValue = d => d[0];
    const yValue = d => d[1];

    const colorValue = d => d[2];

    const rows = df.data

    const size = 500;

    // TODO: when we are compiling this, we should be able to use d3 here...
    const categories = new Set(rows.map(colorValue));
    const isCategory = Boolean(colorName);
    // http://colorbrewer2.org/?type=qualitative&scheme=Set3&n=12
    const colors = [
      'rgba(141,211,199,0.9)',
      'rgba(251,128,114,0.9)',
      'rgba(128,177,211,0.9)',
      'rgba(253,180,98,0.9)',
      'rgba(179,222,105,0.9)',
      'rgba(252,205,229,0.9)',
      'rgba(217,217,217,0.9)',
      'rgba(188,128,189,0.9)',
      'rgba(204,235,197,0.9)',
      'rgba(255,237,111,0.9)',
      'rgba(190,186,218,0.9)',
      'rgba(255,255,179,0.9)',
    ];

    const colorMap = new Map([...categories].map((value, index) => [value, colors[index]]));

    if (isCategory) {
      const legend = $("<ul>").css({ margin: 0, padding: 0, listStyle: 'none' }).appendTo(container);
      $("<span style='margin: 0.25em; font-weight: bold'>").text(df.columns[2]).wrap("<li>").parent().appendTo(legend);
      for(const [category, color] of colorMap.entries()) {
        const item = $("<li>").appendTo(legend);
        $("<div>")
          .css({ width: '20px', height: '20px', display: 'inline-block', background: color, border: '1px solid #000', verticalAlign: 'middle', margin: '0.25em 0.75em'})
          .appendTo(item);
        $("<span>").text(category).appendTo(item);
      }

    }
    const colorBy = isCategory ?
      d => colorMap.get(colorValue(d)) || '#000000' :
      undefined;

    var scatter = new VizGPM.Charts.ScatterPlot({
      root,
      rows,
      size,
      pointRadius: 3,
      margin: {
        bottom: Math.floor(Math.max(size/6, 35)),
        left: Math.floor(Math.max(size/12, 35)),
        top: 0,
        right: 0,
      },
      aesthetics: [{
        name: xName,
        value: xValue,
      }, {
        name: yName,
        value: yValue,
      }],
      // This is currently a custom-hack in the built vizgpm we are using
      colorBy,
      scales: {
        x: VizGPM.Charts.Scales.SCALE_METHOD.linear(),
        y: VizGPM.Charts.Scales.SCALE_METHOD.linear(),
      },
    });

    scatter.render();
  })
  .catch(e => {
    const stack = $("<code>")
      .css({ whiteSpace: "pre", display: "block", color: "red", overflow: "auto" })
      .text(e.stack);
    debugger;
    myCell.append("Error initializing chart:", stack);
  })
}
