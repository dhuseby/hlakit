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

#ram.org 0xFB00

inline load_startup_values()
{
    do
    {
        // load the destination address
        ldx CART_BANK_0

        // load the value
        lda CART_BANK_0

        // store the value
        sta $00,x

        // test to see if we have the end marker
        and $00,x

    } while(not zero)
}

inline calculate_number_of_segs(size, segs, chunks_per_seg)
{
    // initialize y
    ldy #0

    // load the number of 256 byte chunks in the exe
    lda hi(size)

    // divide by the number of chunks in the segment
    ldx chunks_per_seg
    while (not zero) {
        lsr

        // set y to true if any bits are set
        if (carry) {
            ldy #1
        }

        dex
    }

    // decrement y, the zero flag will be set if y was true
    dey
    if(zero) {
        // we need to increment the number of segments by one
        inc
    }

    // store the number of segments
    sta segs
}


// load 256 byte from the cart and store it at the address specified by dest
// NOTE: dest must be a 16-bit address stored in the zero page
inline load_chunk(dest)
{
    ldy #0

    // this loop loads 256 bytes of data
    do
    {
        lda CART_BANK_0
        sta dest
        inc_16(dest)
        iny
    } while(not zero)
}

inline load_segment(seg, dest, chunks_per_seg)
{
    // reset x to have the number of 256 byte chunks per segment
    ldx chunks_per_seg

    // set the cart segment address 
    set_cart_segment_address(seg)

    do
    {
        // load a 256 byte chunk from the cart and store it in RAM
        load_chunk(dest) 

        // decrement the chunk per segment counter
        dex

    } while(not zero)
}

function noreturn secondary_loader()
{
    // zero page variables that get initialized with the startup values
    word exe_size       :$80    // the total number of bytes of the exe
    word exe_location   :$82    // the RAM location of the exe
    byte exe_segment    :$84    // the starting ROM segment number of the exe
    byte chunks_per_seg :$85    // the number of 256 byte chunks per segment

    // when we get here, the cart segment is 0, the counter is 512. now is the
    // time to read in the startup variables.  this will initialize the values
    // for the variables defined above.
    load_startup_values()

    // temporary variables used for loading the exe
    byte num_segs       :$86
    byte cur_seg        :$87
    word cur_write      :$88

    // initialize the number of segments to load
    calculate_number_of_segments(exe_size, num_segs, chunks_per_seg)

    // initialize the current segment we're loading
    lda exe_segment
    sta cur_seg

    // initialize write pointer
    lda exe_location
    sta cur_write

    // load all of the segments
    do 
    {
        // load a segment
        load_segment(cur_seg, cur_write, chunks_per_seg)
      
        // increment the segment address
        inc cur_seg

        // decrement the segment counter
        dec num_segs

    } while(not zero)
    
    // the exe is loaded so do a blind jmp to run it
    jmp (exe_location)
}

#ram.end

