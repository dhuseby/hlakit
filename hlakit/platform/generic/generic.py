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

from hlakit.common.target import Target
from hlakit.common.session import Session, CommandLineError

class Generic(Target):
    
    def __init__(self, cpu=None):
        if not cpu:
            raise CommandLineError("no CPU specified for generic platform")

        super(Generic, self).__init__()

        cpu_spec = Session().get_cpu_spec(cpu)
        if not cpu_spec:
            raise CommandLineError("unknown CPU type: %s" % cpu)

        # get the platform data
        cpu_class = cpu_spec['class']
        cpu_module = 'hlakit.' + cpu_spec['module']
        cpu_symbols = __import__(cpu_module, fromlist=[cpu_class])
        cpu_ctor = getattr(cpu_symbols, cpu_class)

        # initialize the target
        self._cpu = cpu_ctor()

    def lexer(self):
        return self._cpu.lexer()

    def parser(self):
        return self._cpu.parser()

    def pp_lexer(self):
        return self._cpu.pp_lexer()

    def pp_parser(self):
        return self._cpu.pp_parser()

