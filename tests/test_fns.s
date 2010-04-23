function foo()
{
    ldy #0x00
    lda #1K
}

interrupt noreturn main()
{
    ldy #$FF
}

inline bar(baz, qux)
{
    lda #%11010001
}

