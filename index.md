% Introduction
% Copyright (c) 2014 David Huseby <dave@linuxprogrammer.org>

[HLAKit](https://github.com/Wookie/hlakit) is a new compiler for a language based on [NESHLA](http://neshla.sourceforge.net/) (NES High Level Assembler) by Brian Provinciano.  The NESHLA compiler is a Windows-only application targeted only at the NES system and has lots of NES-specific features in both the language and the standard library.  I [ported the original NESHLA to Linux](http://bitbucket.org/wookie/neshla) in 2009 with the idea of extending it, but I soon decided it would be better to start from scratch in Python. HLAKit aims to be a compiler for a more general HLA (high level assembly) language targeted at as many old video game consoles and computers as possible.

The HLAKit compiler is implemented using the [PLY](http://www.dabeaz.com/ply/) Python module to handle all of the scanning and parsing.  The goal is to structure the compiler in such a way that all platform/CPU specific pieces of the language are modular and swappable.  Currently, the list of platform and/or CPU specific parts includes: assembly opcodes, register names, if/while test values, and preprocessor directives.  These will be explained in more detail later on.

Why do this?  An HLA language gives a nice balance between structured programming and assembly language.  It allows you to program using functions, structs, named variables, if-else blocks and loops while still preserving precise, cycle-counted control over the machine.  Unlike C, the HLA understood by the HLAKit compiler uses assembly for the body of functions.  When you are coding for old, 8-bit and 16-bit computers that have precise timing requirements, assembly language is the only way to be sure you are getting the most out of the machine.

### Quick Start for the Impatient

The fastest way to get started with HLAKit is to clone the repo and install it.

```sh
$ git clone git://github.com/Wookie/hlakit.git
$ cd hlakit
$ sudo python ./setup.py install
```

That's it.  You'll have to read the rest of the documentation to learn the language and how to use the compiler.

## The Language <a class="anchor" href="#The_Language" name="The_Language">&nbsp;</a>

The language that the HLAKit compiler understands has many similarities with the C language.  Code blocks and structs are surrounded by curly braces `{ }` and the conditional statements look very similar to what you see in C.  That's where the similarities end though.  The goal of the language is to make writing assembly applications just a tiny bit easier by supporting some of the higher level constructs found in C.  When writing code in the HLAKit language, you will be writing mostly assembly.  But instead of using labels everywhere and hand coding tests and jumps, you can rely on function calls and higher level conditional constructs like `if(set) {} else {}`.

Throughout this documentation you will see used, the terms \"target\", \"family\", \"platform\", and \"CPU\".  For a lot of old hardware, there is a family of machines with slightly different technical specifications and CPU's.  For instance, the Apple II family of computers has nine different varieties--or platforms.  Some of the platforms came with one of several different CPU's.  The platform specifies the set of peripherals, memory layout, and available CPU's.  In a family of machines, there is a platform for each major, distict combination of peripherals and memory layout.  From the software perspective, if the only thing that changes is the CPU, then a new platform is not warranted.  The Apple IIe originally shipped with a standard 6502 but the later \"enhanced\" version had a 65C02.  Even though the chips on the motherboard changed significantly, along with the CPU, from the software perspective, the two machines are identical except for the CPU change.  Therefore the Apple IIe and the enhanced version are the same platform.

A \"target\" is the combination of family, platform, and CPU.  In the HLAKit world, the way a target is specified is:  \<family\>-\<platform\>-\<cpu\>.  When the HLAKit compiler runs, it is compiling for a specific target.  Some examples are AppleII-e-65C02, NES-NTSC-2A03, Gameboy-DMG-LR35902, and Gameboy-GBC-LR35902.  One of the things to remember with this language is that many of the preprocessor directives, conditional tests, and assembly opcodes are platform and/or CPU dependent.  So know what target you are writing for.

