#ines.mapper "NES-NROM"
#ines.mapper 16
#ines.mapper "none"

#ines.mirroring 0
#ines.mirroring "v"
#ines.mirroring "horizontal"

#ines.fourscreen 1
#ines.fourscreen "Y"
#ines.fourscreen "no"

#ines.battery 1
#ines.battery "Y"
#ines.battery "no"

#ines.trainer 1
#ines.trainer "Y"
#ines.trainer "no"

#ines.prgrepeat 4
#ines.chrrepeat 2
#ines.off

#ram.org 0x0200
#ram.org 0xC000, 1K
#ram.end

#rom.org 0xD000
#rom.org 0xE000, 2K
#rom.end

#rom.banksize 1

#define FOO 1

#rom.bank 1
#rom.bank FOO
#rom.bank FOO, 1K

#chr.banksize 4
#chr.bank FOO, 2K
#chr.link "font.chr"
#chr.link "foo.chr", 2K

#tell.bank
#tell.bankoffset
#tell.banksize
#tell.bankfree
#tell.banktype

