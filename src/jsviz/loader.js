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


var cell = element.is('.output_subarea') ? element : element.next();
// When loading from the `iventure-jsviz.js` file we don't have anything async load
// so we can be immediately ready.
window.iventureReady = Promise.resolve();

cell.append('<p>Loaded bundled iventure-jsviz.js</p>');
cell.append('<p>Version ' + iventureJsviz.VERSION + '</p>');
