"""
Copyright (c) 2010-2014 David Huseby. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL COPYRIGHT HOLDERS AND CONTRIBUTORS OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of copyright holders and contributors.
"""

import os
from exceptions import Exception

class Paths(object):

    _shared_state = {}

    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

    def _reset_state(self):
        # we always search the local directory first
        self._search_paths = [ os.getcwd() ]

    def _check_state(self):
        if getattr(self, '_search_paths', None) is None:
            self._reset_state()

    def add_path(self, path):
        self._check_state()
        apath = os.path.abspath(path)
        if not os.path.isdir(apath):
            raise Exception('invalid search path %s' % path)
        self._search_paths.insert(0, apath)

    def resolve_filepath(self, filepath):
        self._check_state()
        if len(filepath) < 1:
            return None

        # if first char is os.sep, we interpret the filepath as being absolute
        if filepath[0] == os.sep:
            apath = os.path.abspath(filepath)
            if os.path.isfile(apath):
                return apath

        # otherwise we try to find the file in the search paths
        else:
            for path in self._search_paths:
                apath = os.path.abspath(os.path.join(path, filepath))
                if os.path.isfile(apath):
                    return apath

        return None

    def dump(self):
        self._check_state()
        import pprint
        print "search paths:"
        pprint.pprint(self._search_paths)


