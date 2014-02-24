% Macros
% Copyright (c) 2014 David Huseby <dave@linuxprogrammer.org>

Along with functions, the HLAKit language also supports macros.  Macros look very similar to functions except that macros start with the `inline` keyword and can take a list of parameters.  Macros are allowed to take paramters because they are expanded inline wherever they are called and the paramters are used for name replacement when the expansion takes place.

#### Syntax:
```
inline LABEL ( PARAMETER_LIST )
{
    // macro body
}
```

#### Examples:
```
inline assign( dest, value )
{
    lda value
    sta dest
}

function foo()
{
    assign( FOO, $0200 )
}
```

When calling a macro in your code, you are not generating a "jump to subroutine" sequence.  Instead, the compiler is expanding the macro in-place and then continuing the compilation.  The above example function `foo` will expand to the following:

```
funcion foo()
{
    lda $0200
    sta FOO
}
```

Macros are very handy for abstracting out common instruction sequences, making assembly language programming more pleasant and a lot less redundant.

