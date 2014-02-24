% Numbers
% Copyright (c) 2014 David Huseby <dave@linuxprogrammer.org>

The HLAKit language supports a number of different types of immediate integer declarations.  Below is a table of the valid ways to declare immediate integers.

Type|Description|Examples|
----|-----------|--------|
decimal|A natural number|123, 3523|
kilo|Base-2 extension `K` meaning multiplied by 1024|1K, 2K, 32K|
hex (C style)|Hexadecimal numbers in the `0x` C style|0x0200, 0xFF|
hex (asm style)|Hexadecimal numbers in the `$` asm style|$0200, $FF|
binary|Binary integers preceded by `%`|%00000010, %11110000|

