% Types
% Copyright (c) 2014 David Huseby <dave@linuxprogrammer.org>

The HLAKit language has a base set of types that is supported on all targets, although the size, in bytes, for each variable may change based on the specified target.  HLAKit supports a C-like `struct` construct for complex data types.

## Basic Types<a class="anchor" href="#Basic_Types" name="Basic_Types">&nbsp;</a>

Type|Size (bytes)|Range|Description|Notes|
----|------------|-----|-----------|-----|
byte|1|0 to 255|8-bit unsigned|
char|1|-128 to 127|8-bit signed|
bool|1|0 to 255|8-bit boolean|Either zero or non-zero
word|2|0 to 65535|16-bit unsigned|16-bit capable CPU's only
dword|4|0 to 4294967295|32-bit unsigned|32-bit capable CPU's only
pointer|1/2/4||8/16/32-bit address|Platform and CPU specific
struct|||Arbitrary complex type|

## Typedef<a class="anchor" href="#Typedef" name="Typedef">&nbsp;</a>

The `typedef` keyword works exactly like the C `typedef`.  It creates a type alias.  This is really only useful for reducing how much you type and making code more readable.

#### Syntax:
```
typedef TYPE LABEL [ARRAY_SIZE]
```

#### Examples:
```
// standard type alias
typedef byte BLAH

// array type alias
typedef char player_name[16]

// struct type alias
typedef struct coords
{
    byte x
    byte y
} coordinates
```

## Struct<a class="anchor" href="#Struct" name="Struct">&nbsp;</a>

The `struct` keyword is used to create new, complex types that are structured containers of named members.  Structs can contain any number of members of any valid type, including other structs.  The type of a struct member can be any of the basic types or an already declared struct type.

#### Syntax:
```
struct LABEL
{
    TYPE LABEL[, LABEL, ...]
}
```

#### Examples:
```
struct time
{
    byte ticks
    byte seconds
    byte minutes
    byte hours
}

struct scrollTo
{
    byte flags
    word x, y
}

struct player
{
    byte sprite
    byte joypad
    struct move
    {
        byte x, y
        byte amount
    } move
    byte anArray[10]
}
```

## Shared<a class="anchor" href="#Shared" name="Shared">&nbsp;</a>

The `shared` keyword is used when declaring new variables and is used to indicate a variable that can be used from multiple execution contexts.  On targets that support interrupts, any variables referenced from both interrupts and the regular code must be declared as `shared` otherwise the HLAKit compiler will output an error.


