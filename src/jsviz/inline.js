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

var myCell = element
window.VizGPMReady = new Promise(resolve => {
  $.getScript('https://probcomp-2.csail.mit.edu/vizgpm/vizgpm.js', function() {
    myCell.append('Loaded VizGPM v' + VizGPM.version);
    $.getScript('https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.4/lodash.js', function() {
      myCell.append('Loaded lodash v' + _.VERSION);
      VizGPM._ = _.noConflict();
      resolve(VizGPM)
    });
  })
})
