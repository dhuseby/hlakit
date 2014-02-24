% Variables
% Copyright (c) 2014 David Huseby <dave@linuxprogrammer.org>

Named variables make coding in assembly much easier.  HLAKit variables are very flexible and do a lot of the hard work for you.  Variables are defined as instances of a specific type and can be assigned to a specific memory location and an initial value.  The optional `shared` keyword flags a variable for use in both interrupt handlers and regular code.  See the section on the <a href="#Shared">`shared`</a> keyword for more details.

#### Syntax:
```
[shared] TYPE LABEL [ARRAY_SIZE] [:ADDRESS] [= VALUE]
```

#### Examples:
```
byte counter
byte initialized_counter = 123
struct coords { byte x, y } myCoords
struct coords theirCoords = { 5, 6 }
byte initialized_array[] = { 1, 2, 3, 4, 5 }
byte flags : $00A0 = %00101100
```

## Arrays<a class="anchor" href="#Arrays" name="Arrays"></a>

When initializing array variables, the array size is optional if a value is being assigned to the variable.  The compiler can calculate the correct size from the assiged value.  Both array values and struct values must be surrounded by curly braces (`{` and `}`).

#### Examples:
```
// initializing a struct variable
struct time t = { 0, 10, 1, 3 }

// declare an array of time structs
struct time history[10]

// initialize array of time structs with implied size
struct time stamps[] =
{
    { 0,  0, 0, 1 },
    { 1,  1, 2, 1 },
    { 0, 10, 1, 3 }
}
```

## Values with Labels<a class="anchor" href="#Values_with_Labels name="Values_with_Lables"></a>

Array variables can be initialized with values that also contain labels for convenience.  This is useful for using direct access to array members instead of indirect, indexed access.  It can mean a significant reduction in CPU cycles when accessing arrays of data.

#### Exmples:
```
// ROM variable initialized with array and labels
byte player_tiles[] =
{
    player_tiles_walk:
    spr00: $01, $02, $03, $04, $05, $06,
    spr01: $07, $08, $43, $44, $41, $42,
    spr02: $11, $12, $54, $11, $42, $32
}
```

## Shared<a class="anchor" href="#Shared" name="Shared"></a>

The `shared` keyword is used when declaring new variables and is used to indicate a variable that can be used from multiple execution contexts.  On targets that support interrupts, any variables referenced from both interrupt handler code and the regular code must be declared as `shared` otherwise the HLAKit compiler will output an error.  The `shared` keyword behaves similarly to the C `volatile` keyword.

#### Examples:
```
// variable  used in both interrupt and regular code
shared byte INPUT_FLAGS = 0
```

## Address Assignment<a class="anchor" href="#Address_Assignment" name="Address_Assignment"></a>

Variable declarations can also contain an explicit address for the variable.  This is mostly useful for memory mapped registers but it is handy for global variables as well.

#### Examples:
```
byte PPU_CNT0       :$2000
byte SPR_DMA        :$4014
byte PPU_IO         :$2007
```


