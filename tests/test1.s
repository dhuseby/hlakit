#todo 'hello'
#todo 'world'
#todo 'one more'
#include 'test2.s'
#setpad "hello, world!"
#setpad 0xDEADBEEF
#align 2K

function blah(boo, bar)
{
    mov x,boo
    add bar,y
}

#ifdef _FOO
#define _BLAH_FOO (1)
#define FOO "BAR"
    #ifdef _BLAH_FOO
    #todo 'inside nested ifdef'
    #endif
#else
    #todo 'inside else block'
#endif

#define _FOO
#ifdef _FOO
#todo 'inside and ifdef block'
#else
#todo 'shouldn\'t be displayed'
#endif
