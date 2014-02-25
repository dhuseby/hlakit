% Atari - Lynx - MOS65SC02
% Copyright (c) 2014 David Huseby <dave@linuxprogrammer.org>

The Atari Lynx target uses the MOS 65SC02 CPU.  This has a slightly different set of opcodes than a standard MOS 6502.  It also differs from just about every other 6502-based machine in that it cannot directly address the cartridge ROM memory.  The Lynx uses a pair of memory mapped read registers that data is read through.  To specify the cartridge ROM address, the Lynx uses an address shift register and an address ripple counter.  The address shift register stores the 8 most-significant bits of the ROM address (bits 12-19).  The address ripple counter stores the 11 least-significant bits of the ROM address (bits 0-10).  Bit 11 in the ROM address is not connected to the ROM.

Every Atari Lynx cartridge has 256 blocks of memory.  The size of each block varies depending on the cartridge.  The address shift register is used to select which block of ROM memory to read from.  The address ripple counter addresses a specific byte in the block.  The address ripple counter can be set to a specific value and then every subsequent read from the memory-mapped read register will increment the address ripple counter.  This allows subsequent reads from the memory-mapped read register to read segments of data from the ROM.

In addition to the address shift register and the address ripple counter, the Atari Lynx has two different memory-mapped read registers.  The two different read registers use differen strobe lines and can therefor be used to talk to two different banks of memory.  There is also the auxilary data in/out (AUDIN) that can act as an additional address line for custom cartridges.

Not every cart uses all bits of the address ripple counter.  Below is a table of possible cartidge configurations.

Total Size|Block Count|Block Size|Bits|Banks|
----------|-----------|----------|----|-----|
64KB|256|256B|0-7|1|
128KB|256|512B|0-8|1|
256KB|256|1KB|0-9|1|
512KB|256|2KB|0-10|1|
1MB|256|2KB|0-10|2|
2MB|512 (+AUDIN)|2KB|0-10|2|

## Preprocessor<a class="anchor" href="#Preprocessor" name="Preprocessor"></a>

### ROM, RAM, Banks

Because the Atari Lynx cannot directly address its cartridge ROM, all code compiled for the Atari Lynx has to be linked and located in the 64KB RAM memory area.  However, to build a full Lynx ROM file, the compiled executable has to be stored in the ROM memory area.  This calls for a two-stage process for building an Atari Lynx game.  It also means that branching almost always has to use relative addresses because so that executable data can be loaded into an arbitrary piece of RAM and executed.

#### #rom.bank 0|1

Selects which ROM bank the compiler is building.

#### #rom.org BLOCK, ADDRESS[, MAX_SIZE]

Sets the current ROM address by specifying the block number, the block address and the max size for the next set of compiled data.  The max size is really there to check assumptions on how much memory the output is taking.  It has no direct relationship to block size or anything.

#### #rom.end

Ends the current block of output.

#### #ram.org ADDRESS[, MAX_SIZE]

Sets the current RAM address by specifying the address and optional max size for the next block of compiled data.  This is used by the compiler for locating and linking executable code.  The max size is there for checking assumptions about the size of the compiled data.

#### #ram.end

Ends the current block of output.

It is likely that you will want to use a Makefile to first compile the code for your Atari Lynx game and then use a separate file to build the final ROM image.  It will take a combination of the following preprocessor directives to specify the correct addressing when doing both stages of the ROM compile.

#### Example Executable:
```
// turn off .lnx header output to get raw binary
#lnx.off

// specify RAM to be from 0x0200 to the start
// of the two video buffers at 0xC038
#ram.org 0x0200, 0xBE38

function noreturn main()
{
    forever
    {
        // the game
    }
}
```

The above example will compile the `main()` function to be located at 0x0200 in RAM and output a raw binary file that does not have the standard .lnx ROM file header.  If the file was called game.hla, the output file would be called game.bin.  We can then use `#incbin` to include the raw binary into the final ROM file.

#### Example ROM:
```
// configure the .lnx file header
#lnx.version 1
#lnx.name "My Game"
#lnx.manufacturer "Me, Myself, and I"
#lnx.rotation "none"

// specify that we have a 512KB cart
#lnx.banks 1
#lnx.block_count 256
#lnx.block_size 2K

// start at bank 0, block 0, counter 0
#rom.bank 0
#rom.org 0,0,2K
#incbin "game.bin"
#rom.end
```

The above example shows how we can use the Atari Lynx specific preprocessor directives to build a final ROM binary with a proper .lnx header.  All of the Lynx preprocessor directives are described below.

### .LNX Header

#### #lnx.version 1|2

Used to specify the version of the .lnx header format.  Version 1 is the only version supported by Mednafen and Handy at the moment.  There is a prosed version 2 that supports a new cart format that uses both the AUDIN and different cart strobes to expand the cart ROM memory out to 2MB.

#### #lnx.name QUOTED_STRING

Used to specify the name of the game in the ROM.

#### #lnx.manufacturer QUOTED_STRING

Used to specify the name of the manufacturer of the ROM.

#### #lnx.rotation QUOTED_STRING

Specifies if the game is to be played in rotated mode.  Valid values are "none", "left" and "right" rotation.

#### #lnx.banks 1|2

Tells HLAKit how many banks this ROM image uses.

#### #lnx.block_count 256|512

Tells HLAKit how many blocks are in each bank.  The standard value is 256, but a cart that uses the AUDIN address line as an extra address line can have 512 blocks.

#### #lnx.block_size VALUE

Specifies the size of each block in the cart.  Valid values are 256, 512, 1K, 2K, 4K.  The 4K value is only possible if the cart uses different read strobes to read from separate memory chips.

#### #lnx.off

Tells the HLAKit compiler to not output a standard .lnx header in the output file.  This is usefull for producing raw binary files that will be later included into a ROM image file.

## Interrupts<a class="anchor" href="#Interrupts" name="Interrupts"></a>

The Atari Lynx supports the same three MOS 6502 interrupts: reset, NMI, and IRQ.  The reset interrupt is also aliased as the "start" interrupt.  The target interrupt keywords for declaring an interrupt are `reset`/`start`, `nmi`, and `irq`.

#### Syntax:
```
interrupt[.reset|start|nmi|irq] LABEL()
{
    // interrupt handler body
}
```

## Conditionals<a class="anchor" href="#Conditionals" name="Conditionals"></a>

The MOS 65SC02 has a 7-bit status register.  Some bits in the status register are used for conditional branching.  The bits used are: C (carry), Z (zero), V (overflow), N (negative).  The target-specific conditional keywords for the Atari Lynx are listed in the table below.  The table also lists the status register flag tested and the opcode that will be generated when the HLAKit compiler encounters the associated keyword.

Condition|Flag|Opcodes|
---------|----|-------|
plus|N|BPL|
positive|N|BPL|
greater|N|BPL|
minus|N|BMI|
negative|N|BMI|
less|N|BMI|
overflow|V|BVC
carry|C|BCS|
nonzero|Z|BNE|
set|Z|BNE|
true|Z|BNE|
1|Z|BNE|
equal|Z|BEQ|
zero|Z|BEQ|
false|Z|BEQ|
unset|Z|BNE|
clear|Z|BNE|
0|Z|BNE|

## Opcodes<a class="anchor" href="#Opcodes" name="Opcodes"></a>

The Atari Lynx MOS 65SC02 is an improved version of the standard MOS 6502.  The table below lists the opcode supported by this target.

Opcode|Address Modes|
------|-------------|

