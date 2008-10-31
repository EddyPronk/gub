#ifndef OOO_WINDEF_H
#define OOO_WINDEF_H

/* Hack arount tools/solar.h BOOL etc disaster */

#if defined (__MINGW32__) && ! defined (BOOL)
#define OOO_BOOL_HACK
#define BOOL WINDEF_BOOL
#define INT32 WINDEF_INT32
#define UINT32 WINDEF_UINT32
#endif /* __MINGW32__ */

#include <../include/windef.h>

#if 0 //def OOO_BOOL_HACK
#undef BOOL
#undef INT32
#undef UINT32
#undef OOO_BOOL_HACK
#endif /* OOO_BOOL_HACK */

#endif /* OOO_WINDEF_H */
