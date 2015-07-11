unfortunately, I haven't touched hlakit in a long time.  I wish I had
stuck with it and finished it.  I would be more than happy to hand it
over to somebody who wants to try to finish it.  My goals for the
project were:

1) normalized the neshla language so that it is an LR(1) language.
2) write a new compiler in Python so that it is easy to hack on.
3) organized the compiler so that it supports multiple back-ends (e.g.
NES, Sega Mastersystem, etc).

I still have all of the documentation and all of the code.  The
current state is that the front end works pretty well.  It can
successfully parse fairly large games into a full AST.  I think I got
hung up on the immediate mode commands like "#ram.org 0xA000" when I
stopped working on it.

I couldn't see it back then, but the solution for handling immediate
mode commands is to make AST nodes for the different types of
immediate mode ops and add them to the AST just like any other piece
of code.  They will pass through the stages of the compiler until the
compiler reaches the stage where they make sense.  So for example:

#rom.org 0x400

function foo() {
  adc $00
}

That would translate to an AST like:

+- ROM { base: 0x400 }
 +- FN { name: "foo" }
  +- ASM { op: "adc", src: "$00", dst: "A", amode: "zp" }

So then when the code generator runs through the tree, it translates
the AST to something like:

+- ROM { base: 0x400 }
 +- BLOCK { name: "foo", dirties: ["S","A"] }
   +- INSTR { op:"php", src:"S", dst:"SP", amode:"implied", bin:0x08 }
   +- INSTR { op:"pha", src:"A", dst:"SP", amode:"implied", bin:0x48 }
   +- INSTR { op:"adc", src:"$00", dst:"A", amode:"zp", bin:0x6500 }
   +- INSTR { op:"pla", src:"SP" dst:"S", amode:"implied", bin:0x68 }
   +- INSTR { op:"plp", src:"SP" dst:"S", amode:"implied", bin:0x28 }

So what happens is that there would be a CPU specific--in this case
6502--code generator that knows what to do with FN and ASM AST nodes.
 It translates fn nodes into BLOCK nodes with the proper
prologue/epilogue.  Then it translates the instr nodes into INSTR
nodes in the body of the BLOCK.  So after code generation, you've got
a global set of root nodes that are all either RAM or ROM nodes
containing a bunch of BLOCK nodes which in turn contain INSTR nodes.

The code optimizer then runs and processes all of the BLOCK nodes,
trying to do keyhole optimization and block re-arranging for maximum
speed.  After it is done, the AST will just be RAM/ROM nodes
containing INSTR nodes.

Then all of that gets handed to the CPU+Platform specific
linker/locator which then goes through building the binary blobs from
the RAM/ROM trees.

The last stage is the platform specific file output.  For NES, that
means generating a .nes ROM file in the correct format.  Other
platforms, like the C64, get a .hex binary image that can be burned
directly to EEPROMs.

Anyway, I got stuck on how to do all of this back when I stopped
working on it.  I now know enough about compilers to finish this, but
I'm super busy on other projects.

I have only written the front-end, but it is still messy.  It needs to
be broken up into multiple smaller stages instead of trying to do
everything in one pass.  If I were to pick this project up again, I'd
focus on rethinking how the data flows through the compiler from front
to back.  The first pass would be a simple pre-processor parser that
just handles "#include X" expressions by loading the included file
into the AST.  Each file gets a FILE AST node with the absolute path
to the file and where it was included from:

FILE { path: "/foo/bar/baz.h", from: { path: "/foo/bar/main.hla",
line: 21 } }

Then under each FILE AST node, would be one LINE node for each line in
the file:

+- FILE {...}
 +- LINE { text: "function foo() {", line: 5 }
 +- LINE { text: "  adc $00", line: 6 }

Then it's just a matter of running the AST through the pipeline.  At
each stage, the AST gets translated into another AST until eventually,
the last stage is just the AST with RAM/ROM and INSTR nodes that gets
handed to the file output stage.

IMO, the overall compiler stages should be:

File IN -> Preprocessor -> Parser -> Code Generator -> Locater -> File O
UT

I think the Session class should be reworked build the pipeline and
expand the stages out into HLAKIT, machine, and cpu specific pieces of
each stage and then "run" each object in the list.  Something like:

HLAKIT File IN -> NES File IN -> 6502 File IN -> HLAKIT Preprocessor
-> NES Preprocessor -> 6502 Preprocessor -> HLA Parser -> NES Parser
-> 6502 Parser -> HLAKIT Code Generator -> NES Code Generator -> 6502
Code Generator -> HLAKIT Locator -> NES Locator -> 6502 Locator ->
6502 File OUT -> NES File OUT -> HLAKIT File OUT

Some of these stages are just NULL stages that do nothing when
compiling for the NES.  For instance the NES File IN, 6502 File IN,
HLAKIT Code Generator and HLAKIT Locator do nothing in this case.
There might be cases where a machine or cpu specific file input object
would do something useful.

At each stage, the code does an in-order tree traversal and handles
the AST node types that it is programmed to handle and ignores the
rest.  So hopefully, by the end of the pipeline, everything has been
reduced down to a list of annotated bytes that can be handed to a
machine and cpu specific file output object for writing to disk in the
appropriate format.

That's pretty much all of my thoughts on the project.  If you want to
take it over, just let me know and I'll give you everything I have an
redirect all of the HLAkit web stuff to your repo.

