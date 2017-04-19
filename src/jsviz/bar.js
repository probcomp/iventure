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

function bar(df) {
  var myCell = element.is('.output_subarea') ? element : element.next();

  // Validate input format.  It should be a pandas dataframe in "split" format:
  // df.to_json(orient="split")

  if (!(df.columns && df.index && df.data)) {
    throw new Error("Incorrect data format");
  }

  if (df.columns.length !== 2) {
    throw new Error("There must be exactly two columns");
  }

  // restrict data to only numeric data
  const rows = df.data.filter( ([,number]) => typeof number === 'number' );

  if (!rows.length) {
    throw new Error("No rows contain numbers in the second column");
  }

  const [ xName, yName ] = df.columns;

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
    const root = $("<div>").prependTo(middleContainer)[0];

    const xValue = d => d[0];
    const yValue = d => d[1];

    class CustomBarChart extends VizGPM.Charts.Histogram {
      _calculateData() {
        if (!this._.aesthetics) return;
        if (this.hasChanged('rows', 'scales')) {
          const {
            rows,
            scales: {x: xScale, y: yScale},
            aesthetics: [
              {value, name: axisName, bins},
              {value: yValue} = {},
            ],
            width,
          } = this._;

          // the histogram chart works as a bar, but it's internal represntation
          // has "x" and "value" so needs a little customization
          this._.chartData = rows.map(row => ({
            x: value(row),
            value: yValue(row),
            rows: new Set([ row ]),
            query: { [axisName]: { $in: [value(row)] } },
          }))

          xScale.domain(this._.chartData.map( d => d.x ));
          yScale.domain([0, _.max(this._.chartData.map(d => d.value))]).nice();
        }
      }
    }

    const size = 500;

    var bar = new CustomBarChart({
      root,
      rows,
      size,
      margin: {
        bottom: Math.max(size/6, 35),
        left: Math.max(size/12, 35),
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
      scales: {
        x: VizGPM.Charts.Scales.SCALE_METHOD.band(),
        y: VizGPM.Charts.Scales.SCALE_METHOD.linear(),
      },
    });

    bar.render();
  })
  .catch(e => {
    const stack = $("<code>")
      .css({ whiteSpace: "pre", display: "block", color: "red", overflow: "auto" })
      .text(e.stack);
    debugger;
    myCell.append("Error initializing chart:", stack);
  })
}
