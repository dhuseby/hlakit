/******************************************************************************
 * NES High Level Assembler Library
 * (c) 2003,2004,2005 Brian Provinciano
 * http://www.bripro.com
 ******************************************************************************
 * NES_RAM.AS
 ******************************************************************************
 * The variables in NES RAM space required by the library functions
 *
 * must be included within a RAM bank
 ******************************************************************************/


/******************************************************************************
 * VIDEO
 ******************************************************************************/
#ifdef _NES_VIDEO_H

// local copies of the ppu control registers
shared byte
_ppu_ctl0, _ppu_ctl1

pointer
_pal_ptr
#endif

/******************************************************************************
 * IO
 ******************************************************************************/
#ifdef _NES_IO_H

// holds bits for each joypad button
shared byte
_joypad, _joypad_prev


#endif

byte pBankA000_prev, pBankA000_cur
/******************************************************************************/
