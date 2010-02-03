/******************************************************************************
 * NES High Level Assembler Library
 * (c) 2003,2004,2005 Brian Provinciano
 * http://www.bripro.com
 ******************************************************************************
 * LIB_RAM.AS
 ******************************************************************************
 * The variables in RAM space required by the library functions
 *
 * must be included within a RAM bank
 ******************************************************************************/

/******************************************************************************
 * STANDARD
 ******************************************************************************/
#ifdef _STD_H

// temporary variables for macros such as the math ones
byte _b_temp
word _w_temp
pointer _p_temp, _jsrind_temp

#ifdef _STD_MATH_H
byte _b_remainder,

_random_value,
_random_ticks
#endif

#endif

/******************************************************************************
 * MEMORY
 ******************************************************************************/
#ifdef _STD_MEMORY_H

// temporary pointers to the memory locations
pointer _mem_src, _mem_dest


#endif
/******************************************************************************/
