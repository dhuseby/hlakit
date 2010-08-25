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

// set the rom address: segment = 0x00, counter=%00000000000, maxsize=2K
#lynx.rom.bank      0
#lynx.rom.org       0x00,%00000000000,2K
#lynx.rom.padding   0x00

// include the micro loader code
#include "micro_loader.s"

// specify which loader function needs encrypting
#lynx.loader micro_loader

/*
 * Include the secondary loader code so that it is immediately following the
 * micro loader on the ROM.  This is necessary because the micro loader doesn't
 * include any code for setting the ROM segment address and just continues with
 * the values left over from the micro loader load.
 */
#include "secondary_loader.s"

#lynx.rom.end

// set the rom address to the second segment
#lynx.rom.org   0x01,%00000000000,510K

// include the main game code.
#include "main.s"

#lynx.rom.end

