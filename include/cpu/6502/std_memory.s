/******************************************************************************
 * NES High Level Assembler Library
 * (c) 2003,2004,2005 Brian Provinciano
 * http://www.bripro.com
 ******************************************************************************
 * STD_MEMORY.AS
 ******************************************************************************
 * Memory/RAM functions
 ******************************************************************************/

// function memcpy()
// function memset()

/******************************************************************************/


/******************************************************************************
 * memcpy( WORD pMemDest,  WORD pMemSrc, REG.Y memSize )
 *
 * memSize==0? memSize=256
 *
 * Registers changed: A, Y
 */
function memcpy()
{
    do {
        dey
        lda (_mem_src),y
        sta (_mem_dest),y
        tya
    } while (nonzero)
}

/******************************************************************************
 * memset( WORD pMemDest, REG.A value, REG.Y memSize )
 *
 * memSize==0? memSize=256
 *
 * Registers changed: A, Y
 */
function memset()
{
    do {
        sta (_mem_dest),y
        dey
    } while (nonzero)
}

/******************************************************************************/
