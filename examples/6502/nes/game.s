/******************************************************************************
 * NESHLA Demo Code
 * (c) 2003-2005 Brian Provinciano
 * http://www.bripro.com
 ******************************************************************************
 * GAME.S
 ******************************************************************************
 * The entire game in one file
 ******************************************************************************/

/******************************************************************************/

#ines.mapper  "none"
#ines.mirroring  "Vertical"
#ines.battery  "no"
#ines.trainer  "no"
#ines.fourscreen "no"
//#ines.prgrepeat  8 // 128K

#rom.banksize  16K
#chr.banksize  8K
#define BANK_MAIN_ENTRY $C000
#define CHR_FONT_BANK $0000

/******************************************************************************/

#include <nes/nes.h>
#include <6502/std.h>

#include "main.h"

// RAM DEFINITIONS
#include "ramdata.s"


/******************************************************************************
 * MAIN CODE     // 16K (2 banks)
 ******************************************************************************/

/******************************************************************************/

#rom.bank   BANK_MAIN_ENTRY
#rom.org   0xC000

#interrupt.start    main
#interrupt.irq  int_irq
#interrupt.nmi  int_nmi

#include "visuals.s"
#include "main.s"

/******************************************************************************/


/*#############################################################################
 #  MMMM  MM  MM MMMM
 # MM  MM MM  MM MM MM
 # MM     MMMMMM MMMM
 # MM  MM MM  MM MM MM
 #  MMMM  MM  MM MM  MM
  #############################################################################*/

#chr.banksize   8K
#chr.bank    CHR_FONT_BANK
#incbin "font2.chr"
#chr.end

/******************************************************************************/
