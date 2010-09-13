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

// set the rom address to the second segment
#lynx.rom.org           1,0

// include the main game code.
#include "main.s"

// TODO: hook into asset compilation system here.

#lynx.rom.end

#lynx.rom.org           0,0x200,512
/* 
 * we can use these 512 bytes for storing things like the size of the initial
 * executable so that the secondary executable can know how much data it
 * needs to load.  this block can also house the initial data for showing
 * the intro and bringing up the game.
 */
#lynx.rom.end


