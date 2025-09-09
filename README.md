## Welcome to the Connectome Toolbox!

This is an open-source toolbox which introduces a novel structural connectivity analysis that allows researchers to compare degrees of similarity between patterns of connectivity of different regions.


### Concepts

The toolbox takes in a NxN matrix of connection strength, such that values in the matrix represent the strength of connection from the row region to the column region. The user also must enter a list of subregions which together form their aggregated region of interest. For example, in a dataset containing all brain subregions, the hippocampus could be composed of dentate gyrus, CA1, CA2, ventral and dorsal CA1, and ventral and dorsal subiculum. This list of subregions will be used to filter the connectome data to generate two new connectomes: One for afferent connections to the region of interest (e.g. connections to the hippocampus) and one for efferent connections from the region of interest (e.g. connections from the hippocampus). Representational similarity analysis is performed on both connectomes, producing a correlation matrix for both. Finally, running multidimensional scaling on these correlation matrices projects the distances in high-dimensional space down to two dimensions, showing which regions cluster together in terms of their connectivity pattern with the aggregated region of interest.

### Getting started

Clone the repository and make a virtual environment with Python 3.10.13. Run `pip install -r requirements.txt`.

To start the app, run `python main.py`.

### Copyright

Copyright 2025 Chris Weinberger

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.