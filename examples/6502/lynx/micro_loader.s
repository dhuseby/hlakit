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
 * ClassicGameDev.com Micro Loader
 * 
 * This is a bare minimum Atari Lynx loader.  It is the only piece of data that
 * must be encrypted using the Lynx RSA public key so that the Lynx has
 * something to load and decrypt on startup.  This is the absolute minimum that
 * an encrypted loader must do.  All it does is set up some system registers
 * and then it loads into the top of RAM, the 256 bytes of ROM data immediately 
 * following the micro loader and then it jumps to the loaded data.  This
 * design allows us to get past the decryption phase as quickly as possible
 * and into a secondary loader that can then load in the game executable and
 * get the game going.
 */

#include <lynx.h>

/* 
 * This tells the compiler that this code will be located in RAM, starting at
 * the address: 0x0200.  Since the Lynx doesn't execute any code from the ROM
 * directly, all code will get loaded into RAM before being executed.  That 
 * means the #ram.org declaration helps the compiler with relative jump
 * addresses.
 */
#ram.org 0x0200

/*
 * The RAM location where the micro loader will load the second stage loader.
 * The micro loader assumes the second stage loader code is 256 bytes or less.
 * The second stage loader is loaded at the very top of RAM so that it can
 * load the game executable into the lowest possible RAM address (0x0200),
 * overwriting the micro loader executable.  After the game executable is
 * loaded into RAM, the second stage will jmp to it and the RAM containing the
 * second stage loader can be reused by the game for other things.
 */
#define SECONDARY_LOADER $FB00

function noreturn micro_loader()
{
    // 1. force Mikey to be in memory
    stz MAPCTL

    // 2. set IODIR the way Mikey ROM does, also force AUDIN to output
    lda #%00010011    
    sta MIKEY_IO_DIRECTION

    // 3. set ComLynx to open collector
    lda #%00000100
    sta MIKEY_SERIAL_CONTROL

    // 4. make sure the ROM is powered on
    lda #%00001000
    sta MIKEY_IO_DATA

    // 5. read in 256 bytes from the cart and store it in RAM
    ldx #0
    do
    {
        // read a byte from the cart, bank 0
        lda CART_BANK_0

        // store it in the desired location
        sta SECONDARY_LOADER,x

        // move destination index
        inx

    } while(not zero)

    // do a blind jmp to the second stage loader
    jmp SECONDARY_LOADER 
}

#ram.end

