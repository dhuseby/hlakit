HLAKit -- A High Level Assembler Toolkit
========================================

Version 0.8.0
Copyright (C) 2010 Dave Huseby <dave@linuxprogrammer.org>

Introduction
------------

HLAKit is based on and inspired by the NESHLA project by Brian Provinciano.  He
created an awesome NES-specific high level assembly (HLA) language that makes
writing NES games much easier than wrangling the cc65 toolchain or any other
NES toolchain out there.

The goal of HLAKit is to create an easily extensible high level assembler
toolkit that supports as many old game consoles as possible.  The high level 
assembly language that the front end parses is derived from the high level 
assembly that NESHLA supported and is mostly exactly the same.  It has been
extended to allow for more cpu and platform specific extensions and to
make processor specific assembly mnemonics easily switchable.

Unlike C, the HLA language doesn't seek to completely abstract the hardware
from the programmer.  Instead the HLA borrows C's curly braced blocks and file
organization mechanics but still requires programmers to write assembly
mnemonics to get things done.  The end result is an assembly language that is
easy to organize and understand, making building large complex software easier
than traditional "flat" assembly.

The other neat addition the HLA language adds is the ability to declare structs
similar to C.  It makes building data structures much more straight forward and
referencing struct members with "dot syntax" (e.g. `foo.bar.baz`) makes life
much easier.  Since structs can be assigned to specific memory addresses,
like any other variable, that enables "dot syntax" access to memory mapped
registers on all supported platforms.

Design
------

Like most compilers, the HLAKit compiler is organized into a front-end and a
back-end.  Both the front-end and back-ends are implemented in an encapsulated,
object-oriented way so that multiple CPU's and platforms can be supported.  It
is fairly easy to extend the HLAKit compiler to a new piece of hardware.

Because the language is just assembly with C-style function semantics and 
flow control, the HLAKit front end has to understand the different assembly
mnemonics for each CPU.  This means that supporting a new CPU requires writing
a lexer and parser class for the HLAKit front-end that can parse the assembly 
mnemonics for the new CPU as well as writing a back-end generator that can emit 
the proper binary for the CPU.

The base HLAKit lexer and parser handle scanning and parsing all of the
core reserved words and basic preprocessor directives (e.g. #ifdef, #define).
Each CPU has a lexer and parser that derives from the base lexer and parser and
adds in the ability to scan and parse the assembly mnemonics, registers, and
CPU-specific preprocessor directives (e.g. #interrupt.start for the 6502). Each
platform has a lexer and parser that derives from the CPU lexer and parser and
adds in the ability to scan and parse platform specific preprocessor directives
(e.g. #nes.mapper for the NES).

The base HLAKit generator is abstract and contains common helper functions as
well as sets the interface for all CPU-specific and platform-specific
generators.  Each CPU has a generator that derives from the base generator and
implements the binary generation for that specific CPU.  Each platform has a 
generator that derives from CPU-specific generator and adds support for handling
the platform-specific link-time preprocessor directives (e.g. `#rom.org`, 
`#rom.banksize`, etc).

Selecting the CPU and/or platform for a project can be done with command line 
arguments.  Use --cpu=6502 and/or --platform=NES for specifying the CPU and 
platform respectively.  If you specify a platform, you don't need to specify
the CPU unless the platform has multiple CPU's (e.g. GBA has a Z80 and an ARM,
NeoGeo AES has a 68K and a Z80).  If you only specify the CPU, then the
"generic" platform will be selected and the resulting .bin file will be a raw
executable file.

Currently Supported CPUs
------------------------

* 6502

Currently Supported Platforms
-----------------------------

Generic
