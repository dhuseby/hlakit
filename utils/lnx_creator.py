#!/usr/bin/env python
"""
LNX Creator
Copyright (c) 2010 David Huseby. All rights reserved.

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

import os
import sys
import optparse
from hlakit.platform.lynx.lnx import Lnx

class CommandLineError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

def parse_command_line(args=[]):

    # parse the command line options
    parser = optparse.OptionParser(version = "%prog 1.0")
    parser.add_option('--bank0-size', default=None, dest='bank0_size',
                      help='specify the bank 0 page size (e.g. 256, 512, 1024, 2048)')
    parser.add_option('--bank1-size', default=None, dest='bank1_size',
                      help='specify the bank 1 page size (e.g. 256, 512, 1024, 2048)')
    parser.add_option('--bank0-file', default=None, dest='bank0_file',
                      help='specify the bank 0 rom image')
    parser.add_option('--bank1-file', default=None, dest='bank1_file',
                      help='specify the bank 1 rom image')
    parser.add_option('--cart-name', default='', dest='cart_name',
                      help='specify the cart name field in the header')
    parser.add_option('--manu-name', default='', dest='manu_name',
                      help='specify the manufacturer name field in the header')
    parser.add_option('--rotation', default='none', dest='rotation',
                      help='specify the rotation (e.g. none, left, rigth)')
    parser.add_option('-o', dest='output_file', default=None,
        help='specify the name of the output file')

    (options, args) = parser.parse_args(args)

    # check for required options
    if not options.bank0_size:
        raise CommandLineError('You must specify the bank 0 page size')
    elif int(options.bank0_size) not in (256, 512, 1024, 2048):
        raise CommandLineError('Bank 0 page size must be one of: 256, 512, 1024, 2048')
   
    if not options.bank0_file:
        raise CommandLineError('You must specify the bank 0 rom file')

    if not options.output_file:
        raise CommandLineError('You must specify the output file')

    if options.bank1_size:
        if int(options.bank1_size) not in (256, 512, 1024, 2048):
            raise CommandLineError('Bank 1 page size must be one of: 256, 512, 1024, 2048')
        if not options.bank1_file:
            raise CommandLineError('You must also specify the bank 1 rom file')

    if options.rotation and options.rotation.lower() not in ('none', 'left', 'right'):
        raise CommandLineError('Rotation can only be "none", "left", or "right"')

    return options 


def build_rom(options):

    # create the rom file
    lnx = Lnx()
    
    # set the bank 0 size
    lnx.set_page_size_bank0(int(options.bank0_size))
    
    # load in the bank 0 rom 
    inf = open(options.bank0_file, 'r')
    if inf:
        lnx.append_bank(inf)
        inf.close()
    else:
        raise RuntimeError('could not open bank 0 rom file: %s' % options.bank0_file)

    if options.bank1_size:
        # set the bank 1 size
        lnx.set_page_size_bank1(int(options.bank1_size))
        
        # load in the bank 1 rom 
        inf = open(options.bank1_file, 'r')
        if inf:
            lnx.append_bank(inf)
            inf.close()
        else:
            raise RuntimeError('could not open bank 1 rom file: %s' % options.bank1_file)
    else:
        lnx.set_page_size_bank1(0)

    # set the cart name
    lnx.set_cart_name(options.cart_name)

    # set the manufacturer name
    lnx.set_manufacturer_name(options.manu_name)

    # set the rotation
    lnx.set_rotation(options.rotation)

    # now save out the ROM file
    outf = open(options.output_file, 'wb+')
    if outf:
        lnx.save(outf)
        outf.close()
    else:
        raise RuntimeError('could not open output file: %s' % options.output_file)

    # output some niceness
    print 'Successfully saved: %s' % options.output_file
    print '%s' % lnx

def main():
    try:
        build_rom(parse_command_line(sys.argv[1:]))
    except CommandLineError, e:
        print >> sys.stderr, 'ERROR: %s' % e
        sys.exit(0)
    except RuntimeError, e:
        print >> sys.stderr, 'ERROR: %s' % e
        sys.exit(0)
    sys.exit(1)

if __name__ == "__main__":
    
    sys.exit(main())
