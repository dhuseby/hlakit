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

The Atari Lynx target initializes several preprocessor variables with the configuration information of the compiler.  This includes the variables: `__TITLE__`, `__MANUFACTURER__`, `__ROTATION__`, `__BANKS__`, `__BLOCK_COUNT__`, and `__BLOCK_SIZE__`.

#### #align NUMBER

Forces the current block to be aligned to the specified boundary.  The argument given must be a power of two.  This is handy for forcing ROM blocks to begin on a cart block boundary.

#### #rom.bank 0|1

Selects which ROM bank the compiler is building.

#### #rom.org BLOCK, ADDRESS[, MAX_SIZE]

Sets the current ROM address by specifying the block number, the block address and the max size for the next set of compiled data.  The max size is really there to check assumptions on how much memory the output is taking.  It has no direct relationship to block size or anything.

#### #rom.end

Ends the current block of output.

#### #rom.blockof( LABEL )

The `#rom.blockof` directive translates to the block ROM block number where the given LABEL is located in the ROM.  This is handy for initializing variables with the block number of where data can be found.

#### #ram.org ADDRESS[, MAX_SIZE]

Sets the current RAM address by specifying the address and optional max size for the next block of compiled data.  This is used by the compiler for locating and linking executable code.  The max size is there for checking assumptions about the size of the compiled data.

#### #ram.end

Ends the current block of output.

#### #loader.org [MAX_SIZE]

The Atari Lynx hardware expects that every game cart being with an RSA encrypted block of executable code.  When the Atari Lynx boots, it reads the encrypted data from the game cart, decrypts it and stores the decrypted executable at $0200 in RAM.  After the decryption is done, it jumps to $0200 to execute the code.  The `#loader.org` directive begins a block of data that will be encrypted that the Atari Lynx can decrypt.  The optional max size argument 

Below is a minimal, encrypted, 1st stage loader.  It does the absolute bare minimum to get past the decryption phase.  It only initializes a few hardware registers to get the Lynx into a sane state and then reads in 256 bytes of data directly following the encrypted loader on the game cart.  After reading the 2nd stage loader into RAM, the 1st stage loader executes the 2nd stage loader.

#### Example Loader:
```
// turn off .lnx header output
#lnx.off

byte RCART_0    : $FCB2 // cart read register
byte IODIR      : $FD8A // I/O direction register
byte IODAT      : $FD8B // I/O data register
byte SERCTL     : $FD8C // serial control register
byte MAPCTL     : $FFF9 // memory map control register

#define 2ND_LOADER  $FB00  // location of 2nd stage loader

// locate loader for 0x0200
#ram.org 0x0200

function noreturn micro_loader()
{
    // 1. enable Mikey access
    stz MAPCTL

    // 2. init IODIR, force AUDIN to output
    lda #%00010011
    sta IODIR

    // 3. set ComLynx to open collector
    lda #%00000100
    sta SERCTL

    // 4. power on ROM
    lda #%00001000
    sta IODAT

    // 5. read in the 2nd stage loader
    ldx #0
    do
    {
        lda RCART_0
        sta 2ND_LOADER,x
        inx
    } while(not zero)

    // execute the 2nd stage loader
    jmp 2ND_LOADER
}

#ram.end
```

#### #loader.end

The `#loader.end` directive ends a block of data that will be encrypted using the Atari Lynx encryption scheme.

The above loader example forms the 1st stage of a two stage loader.  The 2nd stage loader actually loads meta data for the game executable and the hardware details of the ROM.  It then uses that information to load the game executable into RAM at the correct location before executing it.

It is likely that you will want to use a Makefile to first compile the code for your Atari Lynx game and then use a separate file to build the final ROM image.  It will take a combination of the following preprocessor directives to specify the correct addressing when doing both stages of the ROM compile.

#### Example Executable:
```
// turn off .lnx header output to get raw binary
#lnx.off

// locate the main function at 0x0200 in RAM and
// that it cannot bigger than 0xBE38 bytes.
#ram.org 0x0200, 0xBE38

function noreturn main()
{
    forever
    {
        // the game
    }
}

interrupt irq()
{
}

#ram.end
```

The above example will compile the `main()` function to be located at 0x0200 in RAM and output a raw binary file that does not have the standard .lnx ROM file header.  If the file was called game.hla, the output file would be called game.bin.  We can then use `#incbin` to include the raw binary into the final ROM file.  Building a full Atary Lynx ROM image using the two-stage loading scheme, a game executable and a game database is a bit tricky.  Below is a full example.

#### Example ROM:
```
// configure the .lnx file header
#lnx.version 1
#lnx.name "Demo Game"
#lnx.manufacturer "Demo Studio"
#lnx.rotation "none"

// specify that we have a 512KB cart
#lnx.banks 1
#lnx.block_count 256
#lnx.block_size 2K

// select bank 0
#rom.bank 0

// 1st stage loader goes in block 0, counter 0
#rom.org 0, 0
  #loader.org 
  #incbin "micro_loader.bin"
  #loader.end
#rom.end

// 2nd stage loader goes in block 0, counter 256
#rom.org
  // align this block on 256 byte boundary
  #align 0x0100
  #incbin "2nd_loader.bin"
#rom.end

// meta data for 2nd stage loader at block 0, counter 512
#rom.org
  // align this block on 256 byte boundary
  #align 0x0100

  // the size of the executable
  byte EXE_SIZE_LO_ADDR         = $80
  byte EXE_SIZE_LO              = #lo(#sizeof("game.bin"))
  byte EXE_SIZE_HI_ADDR         = $81
  byte EXE_SIZE_HI              = #hi(#sizeof("game.bin"))

  // where the executable should be loaded
  byte EXE_LOC_LO_ADDR          = $82
  byte EXE_LOC_LO               = #lo($0200)
  byte EXE_LOC_HI_ADDR          = $83
  byte EXE_LOC_HI               = #hi($0200)

  // the cart block where executable starts
  byte EXE_BLOCK_ADDR           = $84
  byte EXE_BLOCK                = #rom.blockof(GAME)

  // the number of 256 byte chunks per block
  byte CHUNKS_PER_BLOCK_ADDR    = $85
  byte CHUNKS_PER_BLOCK         = __BLOCK_SIZE__ >> 8

  // the cart block where asset database is located
  byte DATA_BLOCK_ADDR          = $86
  byte DATA_BLOCK               = #rom.blockof(DATA)

  // the end marker
  byte END_ADDR                 = $00
  byte END                      = $00

#rom.end

// main game executable goes in block 1
#rom.org
  // force block to start on block boundary
  #align __BLOCK_SIZE__
GAME:
  #incbin "game.bin"
#rom.end

// the game asset database goes last
#rom.org
  // force block to start on block boundary
  #align __BLOCK_SIZE__
DATA:
  #incbin "data.bin"
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

Because the Atari Lynx cannot directly address the cart ROM memory, it only supports the plain `interrupt` keyword.  It is up to the programmer to manually set the interrupt address registers at run time.  In practice, only the IRQ interrupt is actually used.  The various timers in the device call the IRQ interrupt when they time out.

#### Syntax:
```
interrupt LABEL()
{
    // interrupt handler body
}
```

#### Example
```
interrupt irq()
{
    // handle timer events
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

