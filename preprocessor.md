% Preprocessor
% Copyright (c) 2014 David Huseby <dave@linuxprogrammer.org>

The HLAKit language supports preprocessor directives just like a standard C compiler.  However, the preprocessor in HLAKit is much more flexible and extensible.  It is more accurate to think of the preprocessor directives as immediate mode instructions that get executed while the compiler is working.  The C preprocessor is really only useful for conditional compiles and limited macro-based substitution.  The HLAKit preprocessor does all of that but is also extensible for target-specific extensions.  Things like specifying memory banks, currently address, specifying ROM names, and outputting messages are all things found in the HLAKit preprocessor.

The rest of this section covers the preprocessor directives that are always valid, regardless of the target specified.

## Define<a class="anchor" href="#Define" name="Define"></a>

The `#define` directive is used to both define variables in the preprocessor symbol table, but also to assign values which are used for substitution.  They are included in the language to reduce code duplication and enhance readability.

#### Syntax:
```
#define LABEL [VALUE]
```

#### Examples:
```
// defining boolean true/false integers
#define TRUE 1
#define FALSE 0

// defining a string
#define PROGRAM_VERSION "Version 1.0"

// defining a bitmask
#define ST_VBLANK %10000000

// defining for conditional compile
#define DEBUG_BUILD
```

## Undef<a class="anchor" href="#Undef" name="Undef"></a>

The `#undef` directive deletes a symbol from the preprocessor symbol table.

#### Syntax:
```
#undef LABEL
```

#### Examples:
```
// undefining previously defined integers
#undef TRUE
#undef FALSE
```

## Ifdef, Ifndef, Else, and Endif<a class="anchor" href="#Conditionals" name="Conditionals"></a>

The conditional directives `#ifdef`, `#ifndef`, `#else`, and `#endif` are used for conditional compilation and execution of other preprocessor directives.  Each conditional block begins with either `#ifdef` or `#ifndef` and ends with either and `#else` or `#endif`.

#### Syntax:
```
#ifdef LABEL
#endif

#ifndef LABEL
#endif

#ifdef LABEL
#else
#endif

#ifndef LABEL
#else
#endif
```

#### Examples:
```
#ifdef DEBUG_MODE
#define PROGRAM_VERSION "Version 1.0 (Debug)"
#else
#define PROGRAM_VERSION "Version 1.0 (Release)"
#endif

#ifndef THISHEADER_H
#define THISHEADER_H
// contents of the header
#endif
```

## Todo, Warning, Error, and Fatal Messages<a class="anchor" href="#Messages" name="Messages"></a>

The `#todo`, `#warning`, `#error`, and `#fatal` preprocessor directives are used to output messages, of varying intensities, during compile time.  The `#fatal` directive will output its message, if any, and halt compiler execution.

#### Syntax:
```
#todo [QUOTED_STRING]
#warning [QUOTED_STRING]
#error [QUOTED_STRING]
#fatal [QUOTED_STRING]
```

#### Examples:
```
#ifdef DEBUG_MODE
#warning "This cannot be executable on actual hardware"
#endif

#todo "Oops, still need to implement this."
```

## Include, Incbin, and Usepath<a class="anchor" href="#Include" name="Include"></a>

The `#include` and `#incbin` directives tell the compiler to replace the `#include` or `#incbin` line with the contents of the specified file and then continue compiling.  The `#usepath` directive adds a directory to the compiler's list of directories to search for files specified in `#include` and `#incbin` directives.

#### Syntax:
```
#include QUOTED_STRING
#incbin QUOTED_STRING
#usepath QUOTED_STRING
```

#### Examples:
```
#include "nes.h"
#incbin "sprites.chr"
```

## Lo, Hi, Nylo, Nyhi<a class="anchor" href="#Lo_Hi_Nylo_Nyhi" name="Lo_Hi_Nylo_Nyhi"></a>

The preprocessor supports extracting portions of immediate values as handy shortcuts that save CPU cycles by doing the masking at compile time.  The `#lo` directive translates to an immediate value equal to the lower byte of the word or the lower word of the dword parameter.  The `#hi` directive translates to an immediate value equal to the upper byte of the word or the upper word of the dword parameter.  The `#nylo` directive translates to an immediate value equal to the lower nybble of the byte parameter.  The `#nyhi` directive translates to an immediate value equal to the upper nybble of the byte parameter.

#### Syntax:
```
#lo ( IMMEDIATE )
#hi ( IMMEDIATE )
#nylo ( IMMEDIATE )
#nyhi ( IMMEDIATE )
```

#### Examples:
```
lda #lo($0200)
ora #hi($0200)

#define FOO %01011010
lda #nylo(FOO)
ora #nyhi(FOO)
```

## Sizeof<a class="anchor" href="#Sizeof" name="Sizeof"></a>

The `#sizeof` directive translates to an immediate value equal to the size of the variable.  The variable must have already been declared when the `#sizeof` is encountered.

#### Syntax:
```
#sizeof ( VARIABLE )
```

#### Examples:
```
adc #sizeof(FOO)
```

## Target Specific Preprocessor Directives<a class="anchor" href="#Target_Specific" name="Target_Specific"></a>

As mentioned above, the HLAKit compiler translate the HLAKit language into a target-specific binary.  To do that, there are many parts of the language that change depending on which family, platform, and CPU are specified in the target.  The preprocessor is one of them.  All target-specific preprocessor directives must use the full target prefix: `#<family>.<platform>.<cpu>.<directive>` unless the family, platform, and CPU are either specified on the command line or in the code.  

The preprocessor also automatically defines symbols for `__FAMILY__`, `__PLATFORM__`, `__CPU__`, and `__TARGET__`, that contain the family, platform, CPU and target strings respectively.

### Family, Platform and CPU

Instead of specifying the family, platform, and CPU target on the command line, you may want to use these preprocessor directives to do it in the code.  These allow you to avoid having to type the full `#<family>.<platform>.<cpu>.` prefix for the target-specific preprocessor directives.  These cannot be used to change the target during an execution of the HLAKit compiler.  If the compiler is configured for one target on the command line and it encounters a different target via the `#family`, `#platform`, and `#cpu` directives in the code, it will exit with an error.

#### Syntax:
```
#family QUOTED_STRING
#platform QUOTED_STRING
#cpu QUOTED_STRING
```

#### Examples:
```
#family "NES"
#platform "NTSC"
#cpu "2A03"
```


