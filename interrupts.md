% Interrupts
% Copyright (c) 2014 David Huseby <dave@linuxprogrammer.org>

On targets that support interrupt handers, the `interrupt` class of functions will be available.  These are target specific so consult the documentation for your specific target to see what interrupts are supported and how to use them.  On this page, Iwill assume the target is a generic 6502 based machine.  The 6502 CPU supports three interrupts: reset, NMI, and IRQ.

Interrupt handlers are declared like functions except with the `interrupt` keyword.  There are target-specific extensions to the `interrupt` keyword.  For instance, on the 6502, you can declare an interrupt handler for the NMI interrupt by using the `interrupt.nmi` keyword.

#### Syntax:
```
interrupt[.TARGET_INTERRUPT] LABEL()
{
    // interrupt handler body
}
```

#### Examples:
```
// declare a 6502 reset handler using
// target-specific keyword
interrupt.reset main()
{
    // this code gets executed when the machine
    // comes out of reset
}
```

