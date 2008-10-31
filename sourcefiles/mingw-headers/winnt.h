#ifndef OOO_WINNT_H
#define OOO_WINNT_H

/* Hack arount winnt.h's DELETE etc disaster */

#ifdef __MINGW32__
#define DELETE WINNT_DELETE
#define ERROR_INVALID_TABLE WINNT_ERROR_INVALID_TABLE
#define OPTIONAL WINNT_OPTIONAL
#endif /* __MINGW32__ */

#include <../include/winnt.h>

#ifdef __MINGW32__
#undef DELETE
#undef ERROR_INVALID_TABLE
#undef OPTIONAL
#endif /* __MINGW32__ */

#endif /* OOO_WINNT_H */
