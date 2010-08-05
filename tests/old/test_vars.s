byte a
word b
pointer c
bool c2
shared byte d
byte e: $FFD2
byte f = 1
byte g[2]
bool g2 = true
bool g3[] = { true, false, true }
shared byte h: $FFD3
shared byte i = 0
shared byte i2 = %01110110
shared byte j[2]
shared byte k: $FFD4 = 2
shared byte l[2] : $FFD5 = { 1, 2 }
shared byte m[] : 0x0100 = "Foo"
byte n: 4096 = 3
byte o[]: 1K = "Bar"
byte p[2] = { 3, 4 }
byte q[3]: $D000 = { 5, 6, 7 }
shared byte r : 0xFFFD = 0, s : 0xFFFE = 1K, t
shared byte u[2] = { 8, 9 }, v[] = "Baz", w[]: 0x0500 = { 10, 11, 12 }
typedef byte INT[5] : $C000
INT x
struct time
{
    byte ticks
    byte seconds
    byte minutes
    byte hours
}
struct time y
typedef struct move_t
{
    byte x, y
    byte amount
}
move_t move
typedef struct time time_t
time_t the_time = { ticks: 1, second: 2, minute: 3, hours: 4 }
struct player
{
    byte sprite
    byte joypad
    move_t move
    byte anArray[10]
}
struct player the_player
typedef struct player player_t
player_t z
