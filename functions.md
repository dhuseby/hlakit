% Functions
% Copyright (c) 2014 David Huseby <dave@linuxprogrammer.org>

The HLAKit language supports the declaration of function to help organize your code into manageable chunks.  This is part of what makes it a high level assembler.  Functions are subroutines that return with a "return from subroutine" instruction and therefor use the target-specific subroutine calling mechanism.  One important distinction is that HLAKit functions cannot take any parameters.

#### Syntax:
```
function [noreturn] LABEL()
{
    // function body
}
```

## Return<a class="anchor" href="#Return" name="Return"></a>

With functions, the generation of the "return from subroutine" instruction is automatic for the end of the function body.  However, there are times where you will want to exit a function early.  The `return` keyword can be used to exit a function body early.

#### Examples:
```
// an example 6502 function
function foo()
{
    lda 0x0200,x
    inx
    ora 0x0200,x
    if(zero)
    {
        return
    }
    inx
}
```

## Noreturn<a class="anchor" href="#Noreturn" name="Noreturn"></a>

Functions can also have an optional `noreturn` keyword in the declaration.  This suppresses the output of the "return from subroutine" instructions for the function.

#### Examples:
```
// an example noreturn function
function noreturn do_game()
{
    forever
    {
        do_sound()
        do_input()
        do_graphics()
        tick()
    }
}
```

## Calling Functions<a class="anchor" href="#Calling_Functions" name="Calling_Functions"></a>

Function can be called by their name as they are in other high level languages.  The function call will generate the correct jump opcode for the specified target.  This typically means a "jump to subroutine" instruction will be generated.

#### Example:
```
function inc_global()
{
    lda 0x0200
    ina
    sta 0x0200
}

function bar()
{
    inc_global()
}
```

