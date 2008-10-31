#ifndef OOO_WINGDI_H
#define OOO_WINGDI_H

/* Hack arount wingdi.h's ABSOTULE/RELATIVE disaster */

#ifdef __MINGW32__
#define ABSOLUTE WINGDI_ABSOLUTE
#define ERROR WINGDI_ERROR
#define RELATIVE WINGDI_RELATIVE
#endif /* __MINGW32__ */

#include <../include/wingdi.h>

#ifdef __MINGW32__
#undef ABSOLUTE
#undef ERROR
#undef RELATIVE
#endif /* __MINGW32__ */

#endif /* OOO_WINGDI_H */
