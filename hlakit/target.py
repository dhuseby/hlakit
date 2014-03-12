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

import importlib
from exceptions import NotImplementedError
from symboltable import SymbolTable

class Target(object):

    NAMESPACE = '__TARGET__'
    TARGET = None

    @classmethod
    def targets(cls):
        """Scan family, platform, and cpu modules to build the list of 
        valid targets"""

        targets = []
        families = importlib.import_module('.'.join(['hlakit','families']))
        for family in families.__all__:
            f = importlib.import_module('.'.join(['hlakit','families',family]))
            platforms = getattr(f, 'PLATFORMS')
            for platform in platforms:
                p = importlib.import_module('.'.join(['hlakit','platforms',platform]))
                cpus = getattr(p, 'CPUS')
                for cpu in cpus:
                    targets.append("%s-%s-%s" % (family.lower(), platform.lower(), cpu.lower()))

        return targets


    @classmethod
    def create(cls, t):
        target_id = t.replace('-','_')
        target = importlib.import_module('.'.join(['hlakit','targets',target_id]))
        class_name = getattr(target, 'TARGET_CLASS')
        ctor = getattr(target, class_name)
        cls.TARGET = ctor()
        return cls.TARGET

    def __init__(self, family, platform, cpu):
        SymbolTable().new_namespace( self.NAMESPACE, None )
        SymbolTable().new_symbol( 'family', family, self.NAMESPACE )
        SymbolTable().new_symbol( 'platform', platform, self.NAMESPACE )
        SymbolTable().new_symbol( 'cpu', cpu, self.NAMESPACE )

    def scan(self, f):
        raise NotImplementedError('Target.scan not implemented')

    @classmethod
    def family(cls):
        return SymbolTable().lookup_symbol( 'family', cls.NAMESPACE )

    @classmethod
    def platform(cls):
        return SymbolTable().lookup_symbol( 'platform', cls.NAMESPACE )

    @classmethod
    def cpu(cls):
        return SymbolTable().lookup_symbol( 'cpu', cls.NAMESPACE )


