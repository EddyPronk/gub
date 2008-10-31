#ifndef OOO_WINDEF_H
#define OOO_WINDEF_H

/* Hack arount tools/solar.h BOOL etc gdisaster */

#ifdef __MINGW32__
#define BOOL WINDEF_BOOL
#define INT32 WINDEF_INT32
#define UINT32 WINDEF_UINT32
#endif /* __MINGW32__ */

#include <../include/windef.h>

#if 0 //def __MINGW32__
#undef BOOL
#undef INT32
#undef UINT32
#endif /* __MINGW32__ */

#endif /* OOO_WINDEF_H */
