% Conditionals
% Copyright (c) 2014 David Huseby <dave@linuxprogrammer.org>

One of the most useful features of the HLAKit language is teh ability to use conditional statements to control program flow.  They simplify and speed up coding, enhance code readability, and alleviate the need for extensive labeling.

The majority of conditional branches in assembly language tend to be straight forward jumps, calling for countless labels.  The labels cause the code to lose structure and it becomes tedious to understand the flow of execution.  HLAKit supports `if`, `else`, `while`, `do while`, `forever`, and `switch case`, expressions.  The test statement for each conditional is target specific so you will need to know which kinds of tests you can use on your target.

Each of the supported conditionals is explained in detail in the following sections.

## If, Else<a class="anchor" href="#If_Else" name="If_Else"></a>

The `if else` conditional allows for conditional execution and an optional alternate block to execute.

#### Syntax:
```
if ( TARGET_TEST_STATEMENT )
{
    // body to execute if test is true
}
[else
{
    // optional body to execute if test is false
}]
```

An example of a 6502 (NES) `if else` is given below.

#### Examples:
```
assign( player.joypad, #0 )
poll_joystick0()
and #BUTTON_B

if(set)
{
    or( player.joypad, #BUTTON_UP )
}
else
{
    and_8( player.joypad, #BUTTON_UP)
}
```

## While<a class="anchor" href="#While" name="While"></a>

The `while` conditional creates a loop that executes until the test is no longer true.

#### Syntax:
```
while ( TARGET_TEST_STATEMENT )
{
    // body to execute while test is true
}
```

An example of a 6502 (NES) `while` is given below.

#### Examples:
```
poll_joystick0()
while(set)
{
    // do something

    poll_joystick0()
}
```

## Do, While<a class="anchor" href="#Do_While" name="Do_While"></a>

The `do while` conditional creates a loop that executes once first before testing the condition.  It will continue to execute as long as the test is true.

#### Syntax:
```
do
{
    // body to execute while test is true
} while ( TARGET_TEST_STATEMEN )
```

An example of a 6502 (NES) `do while` is given below.

#### Example:
```
do
{
    lda PPU.STATUS
} while( is plus )
```

## Forever<a class="anchor" href="#Forever" name="Forever"></a>

The `forever` conditional creates an endless execution loop.  It is possible to exit a `forever` loop using a `return` if the loop is in a function or by using some other jump instruction to get outside the loop.

#### Syntax:
```
forever
{
    // body to execute endlessly
}
```

An example of a 6502 (NES) `forever` loop is given below.

#### Examples:
```
interrupt.reset main()
{
    forever
    {
        // main game loop
    }
}
```

## Switch, Case, Default<a class="anchor" href="#Switch_Case_Default" name="Switch_Case_Default"></a>

The `switch` and `case` conditionals are used to compare a given register with multiple values and execute different sequences of code based on the value of the register.  If none of the cases match the value of the register the default block will be executed.  If no `default` case is given, then execution will resume after the `switch` block.

Note that unlike C, there is no break keyword.  Switch statements in HLAKit are a shorthand for `if .. else if .. else` sequences.  The block of code associated with each `case` does not fall through to the next `case`.

#### Syntax:
```
switch ( reg.TARGET_REGISTER )
{
    case IMMEDIATE
    {
        // body of case
    }
    [default
    {
        // body of optional default case
    }]
}
```

Each target has its own specific set of registers.  The test statement for the `switch` conditional begins with `reg.` followed by a target specific register name.  An example of a 6502 (NES) `switch case default` is given below.

#### Examples:
```
ldx foo
switch ( reg.x )
{
    case #12
    {
        lda #23
        ora bar
    }
    case #34
        lda #12

    default
    {
        lda #0
    }
}
```

