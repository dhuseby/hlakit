/******************************************************************************
 * NES High Level Assembler Headers
 * (c) 2003 Brian Provinciano
 * http://www.bripro.com
 ******************************************************************************
 * NES_AUDIO.H
 ******************************************************************************
 * NES audio registers, defines and macros
 ******************************************************************************/
#ifndef _NES_AUDIO_H
#define _NES_AUDIO_H
/******************************************************************************/

/******************************************************************************
 * AUDIO
 ******************************************************************************/

// FOR THOSE WHO LIKE THE UNDERSCRORE STYLE
byte SQUAREWAVEA_CNT0       :$4000
byte SQUAREWAVEA_CNT1       :$4001
byte SQUAREWAVEA_FREQ0      :$4002
byte SQUAREWAVEA_FREQ1      :$4003

// FOR THOSE WHO LIKE THE STRUCTURED '.' STYLE
enum SQUAREWAVEA {
    CNT0                    = $4000,
    CNT1                    = $4001,
    FREQ0                   = $4002,
    FREQ1                   = $4003
}


byte SQUAREWAVEB_CNT0       :$4004
byte SQUAREWAVEB_CNT1       :$4005
byte SQUAREWAVEB_FREQ0      :$4006
byte SQUAREWAVEB_FREQ1      :$4007

enum SQUAREWAVEB {
    CNT0                    = $4004,
    CNT1                    = $4005,
    FREQ0                   = $4006,
    FREQ1                   = $4007
}


byte TRIANGLEWAVE_CNT0      :$4008
byte TRIANGLEWAVE_CNT1      :$4009
byte TRIANGLEWAVE_FREQ0     :$400A
byte TRIANGLEWAVE_FREQ1     :$400B

enum TRIANGLEWAVE {
    CNT0                    = $4008,
    CNT1                    = $4009,
    FREQ0                   = $400A,
    FREQ1                   = $400B
}


byte NOISE_CNT0             :$400C
byte NOISE_CNT1             :$400D
byte NOISE_FREQ0            :$400E
byte NOISE_FREQ1            :$400F


byte PCM_CNT                :$4010
byte PCM_VOLUMECNT          :$4011
byte PCM_ADDRESS            :$4012
byte PCM_LENGTH             :$4013


byte SND_CNT                :$4015

enum SNDENABLE {
    SQUARE_0                = %00000001,
    SQUARE_1                = %00000010,
    TRIANGLE                = %00000100,
    NOISE                   = %00001000,
    DMC                     = %00010000
}


/******************************************************************************/



/******************************************************************************/
#endif
/******************************************************************************/
