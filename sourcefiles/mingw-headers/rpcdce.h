#ifndef OOO_RPCDCE_H
#define OOO_RPCDCE_H

/* Hack arount rpcdce.h's OPTIONAL disaster */

#ifdef __MINGW32__
#define OPTIONAL RPCDCE_OPTIONAL
#endif /* __MINGW32__ */

#include <../include/rpcdce.h>

#ifdef __MINGW32__
#undef OPTIONAL
#endif /* __MINGW32__ */

#endif /* OOO_RPCDCE_H */
