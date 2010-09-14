/* 
 * HLAKit
 * Copyright (c) 2010 David Huseby. All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without modification, are
 * permitted provided that the following conditions are met:
 * 
 *    1. Redistributions of source code must retain the above copyright notice, this list of
 *       conditions and the following disclaimer.
 * 
 *    2. Redistributions in binary form must reproduce the above copyright notice, this list
 *       of conditions and the following disclaimer in the documentation and/or other materials
 *       provided with the distribution.
 * 
 * THIS SOFTWARE IS PROVIDED BY DAVID HUSEBY ``AS IS'' AND ANY EXPRESS OR IMPLIED
 * WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
 * FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL DAVID HUSEBY OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
 * ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 * 
 * The views and conclusions contained in the software and documentation are those of the
 * authors and should not be interpreted as representing official policies, either expressed
 * or implied, of David Huseby.
 */

/*
 * ClassicGameDev.com Example Atari Lynx Game
 */

// configure the .lnx header
#lnx.page_size_bank0    2K  // 512K bank size
#lnx.page_size_bank1    0   // there is only one bank
#lnx.version            1
#lnx.cart_name          "CGD Demo Game"
#lnx.manufacturer_name  "ClassGameDev.com"
#lnx.rotation           "none"

#include <lynx.h>

// make sure we're in bank 0 and set padding to 0
#lynx.rom.bank          0
#lynx.rom.padding       0


///////////////////////////////////////////////////////////////////////////////
// 1ST STAGE MICRO-LOADER SEGMENT
//
// set the rom address: segment=0, counter=0, maxsize=256 the 256 bytes means 
// that our loader can be decrypted in a single call to the RSALoad system rom 
// function.
#lynx.rom.org           0,0,256

// include the micro loader code
#include "micro_loader.s"

// end the chunk of rom with the micro loader
#lynx.rom.end

// specify which loader function needs encrypting
#lynx.loader micro_loader


///////////////////////////////////////////////////////////////////////////////
// 2ND STAGE SECONDARY LOADER SEGMENT
//
// the micro loader assumes the secondary loader is in the 256 immediately 
// following the encrypted micro loader and is no more than 256 bytes long.
// the micro loader will load this function into upper memory and jump to it.
#lynx.rom.org           0,0x0100,256
/*
 * Include the secondary loader code so that it is immediately following the
 * micro loader on the ROM.  This is necessary because the micro loader doesn't
 * include any code for setting the ROM segment address and just continues with
 * the values left over from the micro loader load.
 */
#include "secondary_loader.s"

#lynx.rom.end


///////////////////////////////////////////////////////////////////////////////
// STARTUP VALUES SEGMENT
//
// we use the 512 bytes after the 1st and 2nd stage loader to store startup
// values that the secondary loader and the main game executable use.
#lynx.rom.org           0,0x200,512

// each startup variable is defined using a byte to specify where it should
// get loaded into the zero page, and the value that should get loaded there

// the size of the game executable
byte    GAME_EXE_SIZE_LO_ADDR   = $80
byte    GAME_EXE_SIZE_LO        = lo(sizeof(main) + sizeof(irq))
byte    GAME_EXE_SIZE_HI_ADDR   = $81
byte    GAME_EXE_SIZE_HI        = hi(sizeof(main) + sizeof(irq))

// the location where the game executable should be loaded
byte    GAME_EXE_LOC_LO_ADDR    = $82
word    GAME_EXE_LOC_LO         = lo($0200)
byte    GAME_EXE_LOC_LO_ADDR    = $83
word    GAME_EXE_LOC_LO         = hi($0200)

// the cart segment address of the game executable
byte    GAME_EXE_SEGMENT_ADDR   = $84
byte    GAME_EXE_SEGMENT        = $01

// the number of chunks per cart segment
byte    CART_CHUNKS_PER_SEG_ADDR = $85
byte    CART_CHUNKS_PER_SEG     = $08

// the end marker
byte    END_ADDR                = $00
byte    END                     = $00

#lynx.rom.end


///////////////////////////////////////////////////////////////////////////////
// MAIN EXECUTABLE SEGMENT
//
// set the rom address to the second segment
#lynx.rom.org           1,0

// include the main game code.
#include "main.s"

// TODO: hook into asset compilation system here.

#lynx.rom.end


