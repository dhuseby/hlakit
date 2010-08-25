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
 * ClassicGameDev.com Secondary Loader
 *
 * This secondary loader contains the logic for loading the main game executable
 * into RAM and then executing it.  This loader is loaded at the top of RAM so
 * that it can load the game executable over the micro loader at 0x0200.  
 * When the secondary loader starts, the ROM cart segment address latch is equal 
 * to 0x00 and the 11-bit address counter is equal to 307.  The reason is that 
 * the micro loader is 51 bytes long so after the micro loader gets loaded and
 * decrypted, the address counter is equal to 51.  The micro loader then loads
 * the 256 byte long secondary loader which leaves the address counter equal to
 * 307.
 *
 * The reason this is important is because the game executable will most likely
 * not fit in the remaining 1741 bytes (2048 - 307) in the ROM segment and
 * therefore the secondary loader will need to set the segment address to load
 * the entire game executable.
 */

#include <lynx.h>

/* 
 * This tells the compiler that this code will be located in RAM, starting at
 * the address: 0x0200.  Since the Lynx doesn't execute any code from the ROM
 * directly, all code will get loaded into RAM before being executed.  That 
 * means the #ram.org declaration helps the compiler with relative jump
 * addresses.
 */
#ram.org 0xFB00

/*
 * The RAM location where the secondary loader will load the game executable.
 */
#define GAME_EXECUTABLE $0200

/*
 * Zero page variable used to store the RAM page address the secondary loader
 * is currently loading the game executable into.  The game executable get
 * loaded into RAM at 0x0200.
 */
byte LOAD_PAGE_ADDR_LSB :$0080 = 0x00
byte LOAD_PAGE_ADDR_MSB :$0081 = 0x02
byte CART_SEGMENT_ADDR  :$0082 = 0x01

function noreturn secondary_loader()
{
    /* 
     * TODO: figure out a way to dynamically calculate the game executable
     *       size and pass it to the secondary_loader so that it knows how
     *       much data it needs to load.
     */
     
    // only load 8 pages which is 1 ROM segment
    ldx #8

    // the game executable resides in segment 1
    set_cart_segment_address(0x01)

    do 
    {
        ldy #0

        // this loop loads 256 bytes of data
        do
        {
            lda CART_BANK_0
            sta (LOAD_PAGE_ADDR_LSB),y
            iny
        } while(not zero)

        // move the load page address to the next page
        inc LOAD_PAGE_ADDR_MSB

        dex

    } while(not zero)
    
    // do a blind jmp to the game executable
    jmp GAME_EXECUTABLE
}

#ram.end

