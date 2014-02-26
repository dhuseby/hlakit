/******************************************************************************
 * NES High Level Assembler Headers
 * (c) 2003 Brian Provinciano
 * http://www.bripro.com
 ******************************************************************************
 * NES_MEMORY.H
 ******************************************************************************
 * Memory/RAM routines
 *
 * Functions defined in std_memory.as
 * To use them, you must include std_memory.as in one of your ROM code banks
 * as well as use std_ram.as and nes_ram.as
 ******************************************************************************/
#ifndef _NES_MEMORY_H
#define _NES_MEMORY_H
/******************************************************************************/

/******************************************************************************
 * size==0? size=256
 *
 * Registers changed: A, X
 */
inline vram_memcpy_inline( src, size )
{
    ldx #0
    do {
        lda src,x
        vram_write_a()
        inx
        cpx size
    } while (nonzero)
}

/******************************************************************************
 * size==0? size=256
 *
 * Registers changed: A, X
 */
inline vram_memcpy_rev_inline( src, size )
{
    ldx size
    do {
        dex
        lda src,x
        vram_write_a()
        txa
    } while (nonzero)
}


/******************************************************************************
 * copies all nonzero bytes to the vram
 * size==0? size=256
 *
 * Registers changed: A, X
 */
inline vram_maskcpy_inline( src, size )
{
    ldx #0
    do {
        lda src,x
        if (zero) {
            vram_read_a()
        } else {
            vram_write_a()
        }
        inx
        cpx size
    } while (nonzero)
}

/******************************************************************************/
#endif
/******************************************************************************/
