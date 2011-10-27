"""
HLAKit
Copyright (c) 2010-2011 David Huseby. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY DAVID HUSEBY ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL DAVID HUSEBY OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of David Huseby.
"""

import pydot

class PPGraph(object):

    def __init__(self, fname, ast):
        self._fname = fname
        self._graph = self._build_graph(ast)

    def _build_subgraph(self, ast):
        subg = pydot.Subgraph('')
        
        if isinstance(ast, tuple):
            if isinstance(ast[1], list):
                # has children
                root = pydot.Node(ast[0])
                subg.add_node(root)
                for n in ast[1]:
                    node = pydot.Node(n[0])
                    subg.add_node(node)
                    subg.add_edge(pydot.Edge(root, node))
                    subg.add_subgraph(self._build_subgraph(n))
            else:
                name = ast[0]
                for i in xrange(1, len(ast)):
                    name += ' %s' % ast[i]
                root = pydot.Node(name)
                subg.add_node(root)
        else:
            root = pydot.Node('node_' + ast)
            subg.add_node(root)

        return subg

    def _build_graph(self, ast):
        graph = pydot.Dot(self._fname.split('.')[0], graph_type='graph')
        graph.add_subgraph(self._build_subgraph(ast))
        return graph

    def save(self):
        self._graph.write_pdf(self._fname)
        
