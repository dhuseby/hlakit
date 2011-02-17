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

#ifndef _LYNX_H
#define _LYNX_H

// Atary Lynx System Registers

// Cart I/O
byte CART_BANK_0            :$FCB2      // uses CART0/ as strobe
byte CART_BANK_1            :$FCB3      // uses CART1/ as strobe

// Mikey

/* System Control 1 
 *
 * B7-B2 = unused
 * B1 = power (1 = on)
 * B0 = cart address strobe and address counter reset
 */
byte MIKEY_SYSTEM_CONTROL   :$FD87

/* I/O Direction/Data Registers
 *
 * B7 = NC
 * B6 = NC
 * B5 = NC
 * B4 = audin input
 * B3 = rest output
 * B2 = noexp input
 * B1 = Cart Address Data output (0 turns cart power on)
 * B0 = External Power input (R0M sets it to output, you must set it to input)
 *
 * For setting the direction 0 = input, 1 = output.  When the Lynx comes out of
 * reset, all bits are set to 0. Only bits set for input are valid for reading 
 * from the DATA register.
 */
byte MIKEY_IO_DIRECTION     :$FD8A      // direction control register
byte MIKEY_GPIO             :$FD8B      // general purpose I/O register

/* Serial Control Register
 *
 * Write:
 * B7 = TXINTEN transmitter interrupt enable
 * B6 = RXINTEN receive interrupt enable
 * B5 = 0 (for future compatibility)
 * B4 = PAREN xmit parity enable (if 0, PAREVEN is the bit sent)
 * B3 = RESETERR reset all errors
 * B2 = TX0PEN 1 open collector driver, 0 = TTL driver
 * B1 = TXBRK send a break (for as long as the bit is set)
 * B0 = PAREVEN send/rcv even parity
 *
 * Read:
 * B7 = TXRDY transmitter buffer empty
 * B6 = RXRDY receive character ready
 * B5 = TXEMPTY transmitter totaiy done
 * B4 = PARERR received parity error
 * B3 = 0VERRUN received overrun error
 * B2 = FRAMERR received framing error
 * B1 = RXBRK break recieved (24 bit periods)
 * B0 = PARBIT 9th bit
 *
 * When the Lynx comes out of reset, all bits are set to 0.
 */
byte MIKEY_SERIAL_CONTROL   :$FD8C

/* 
 * Mikey ROM Functions
 *
 * You can call these functions using code like:
 *     jsr #MIKEY.RSA_LOAD
 */
#define SET_CART_SEGMENT_ADDRESS    $FE00
#define RSA_LOAD                    $FE4A

/* Mikey Memory Map Control Register
 *
 * Mikey Reset: 0 0 0 0 0 0 0 0
 * Mikey Access: R/W
 * Suzy Reset: X X X X X X X 0
 * Suzy Access: W
 *
 * Bits: 7 6 5 4 3 2 1 0
 *       | | | | | | | |
 *       | | | | | | | +- Suzy Interface Memory Space 
 *       | | | | | | +--- Mikey Interface Memory Space
 *       | | | | | +----- System ROM
 *       | | | | +------- CPU Vector Registers
 *       | | | +--------- Reserved
 *       | | +----------- Reserved
 *       | +------------- Reserved
 *       +--------------- Sequential Access Disable
 */
byte MIKEY_MEMORY_MAP_CONTROL   :$FFF9

/* 
 * Macro for setting the cart segment address.  The cart segment address is
 * stored in an 8-bit shift register controlled by the cart address data bit
 * and the cart address data strobe.  The shift register clocks in the value
 * of the cart address data bit on the rising edge (0 to 1) of the cart
 * address data strobe.  The cart address data strobe is also the reset signal
 * for the address counter, so after setting the cart segment address the
 * address counter will always be 0.
 */
inline set_cart_segment_address(addr)
{
    // put the address in the accumulator
    lda #addr

    // call the ROM code function
    jsr SET_CART_SEGMENT_ADDRESS
}

#endif
