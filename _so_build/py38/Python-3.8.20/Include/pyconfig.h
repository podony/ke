/* Minimal pyconfig.h for cross-compiling Cython CPython 3.8 extensions (aarch64) */
#ifndef PY_CONFIG_H
#define PY_CONFIG_H
#define SIZEOF_VOID_P 8
#define SIZEOF_SIZE_T 8
#define SIZEOF_LONG 8
#define SIZEOF_OFF_T 8
#define HAVE_LONG_LONG 1
#define HAVE_UNISTD_H 1
#define HAVE_STDINT_H 1
#define SIZEOF_INT 4
#define SIZEOF_SHORT 2
#define SIZEOF_CHAR 1
#define SIZEOF_DOUBLE 8
#define SIZEOF_FLOAT 4
#define SIZEOF_Py_ssize_t 8
#define SIZEOF_TIME_T 8
#define SIZEOF_PID_T 4
#define HAVE_STDDEF_H 1
#define ALIGNOF_SIZE_T 8
#define ALIGNOF_LONG 8
#define ALIGNOF_DOUBLE 8
#define ALIGNOF_Py_ssize_t 8
#define PY_FORMAT_SIZE_T "z"
#define PY_FORMAT_UINT64 "K"
#define PY_FORMAT_INTPTR "k"
#define PY_FORMAT_SIZE_T "z"
#define PY_UINT64_T "unsigned long"
#define PY_INT64_T "long"
#define PY_FORMAT_INTPTR "l"
#define PY_FORMAT_UINTPTR "K"
#define PY_FORMAT_LONG "l"
#endif
