
# Raspberry Pi cross compilation

To future me, or you

After a long time banging my head against this problem it is finally starting to
come together, and I would like to take the time to document this to ail future
attempts at updating and supporting raspberry Pi. This is because Pi's are
difficult, we are required to support armv6, which, is not supported by the
default Debian multi-arch setup, and hence requires us to use a custom toolchain.


This is nothing new, we were using a custom toolchain previously also.

However, moving on to C++, we (I) ran into a few issues.

1. Multiple installed libc versions are a bad idea, but is handled beautifully
   by the native debian multi-arch cross compilers (I don't know how they do
   this yet, and I don't have the time to find out, but it is beautiful).

2. The existing cross-compiler toolchain we used from Bootlin worked fine for us
   for a long time (why we will get to below) [1]

3. Old setup was working, but it was rigid.

# What to do

The libc and libstcxx versions on the rasperry pi OS we are supporting _do have
to_ match the version of the libraries in our custom cross-compiler. There is no
way around this (due to us linking to existing libraries on the device).

# Tricks of the trade

## Check the cross-compiler configuration

This can be done using:

```console
pi@raspberrypi:~$ echo | gcc -xc++ -E -v -
Using built-in specs.
COLLECT_GCC=gcc
Target: arm-linux-gnueabihf
Configured with: ../src/configure -v --with-pkgversion='Raspbian 8.3.0-6+rpi1' --with-bugurl=file:///usr/share/doc/gcc-8/README.Bugs --enable-languages=c,ada,c++,go,d,fortran,objc,obj-c++ --prefix=/usr --with-gcc-major-version-only --program-suffix=-8 --program-prefix=arm-linux-gnueabihf- --enable-shared --enable-linker-build-id --libexecdir=/usr/lib --without-included-gettext --enable-threads=posix --libdir=/usr/lib --enable-nls --enable-bootstrap --enable-clocale=gnu --enable-libstdcxx-debug --enable-libstdcxx-time=yes --with-default-libstdcxx-abi=new --enable-gnu-unique-object --disable-libitm --disable-libquadmath --disable-libquadmath-support --enable-plugin --with-system-zlib --with-target-system-zlib --enable-objc-gc=auto --enable-multiarch --disable-sjlj-exceptions --with-arch=armv6 --with-fpu=vfp --with-float=hard --disable-werror --enable-checking=release --build=arm-linux-gnueabihf --host=arm-linux-gnueabihf --target=arm-linux-gnueabihf
Thread model: posix
gcc version 8.3.0 (Raspbian 8.3.0-6+rpi1)
COLLECT_GCC_OPTIONS='-E' '-v'  '-mfloat-abi=hard' '-mfpu=vfp' '-mtls-dialect=gnu' '-marm' '-march=armv6+fp'
 /usr/lib/gcc/arm-linux-gnueabihf/8/cc1plus -E -quiet -v -imultilib . -imultiarch arm-linux-gnueabihf -D_GNU_SOURCE - -mfloat-abi=hard -mfpu=vfp -mtls-dialect=gnu -marm -march=armv6+fp
ignoring duplicate directory "/usr/include/arm-linux-gnueabihf/c++/8"
ignoring nonexistent directory "/usr/local/include/arm-linux-gnueabihf"
ignoring nonexistent directory "/usr/lib/gcc/arm-linux-gnueabihf/8/../../../../arm-linux-gnueabihf/include"
#include "..." search starts here:
#include <...> search starts here:
 /usr/include/c++/8
 /usr/include/arm-linux-gnueabihf/c++/8
 /usr/include/c++/8/backward
 /usr/lib/gcc/arm-linux-gnueabihf/8/include
 /usr/local/include
 /usr/lib/gcc/arm-linux-gnueabihf/8/include-fixed
 /usr/include/arm-linux-gnueabihf
 /usr/include
End of search list.
# 1 "<stdin>"
# 1 "<built-in>"
# 1 "<command-line>"
# 1 "/usr/include/stdc-predef.h" 1 3 4
# 1 "<command-line>" 2
# 1 "<stdin>"
COMPILER_PATH=/usr/lib/gcc/arm-linux-gnueabihf/8/:/usr/lib/gcc/arm-linux-gnueabihf/8/:/usr/lib/gcc/arm-linux-gnueabihf/:/usr/lib/gcc/arm-linux-gnueabihf/8/:/usr/lib/gcc/arm-linux-gnueabihf/
LIBRARY_PATH=/usr/lib/gcc/arm-linux-gnueabihf/8/:/usr/lib/gcc/arm-linux-gnueabihf/8/../../../arm-linux-gnueabihf/:/usr/lib/gcc/arm-linux-gnueabihf/8/../../../:/lib/arm-linux-gnueabihf/:/lib/:/usr/lib/arm-linux-gnueabihf/:/usr/lib/
COLLECT_GCC_OPTIONS='-E' '-v'  '-mfloat-abi=hard' '-mfpu=vfp' '-mtls-dialect=gnu' '-marm' '-march=armv6+fp'
```

And gives us a few key data-points, like the sysroot the compiler is configured
to use. This is the place in which we want to install our packages, in order to
have the compiler and linker pick them up automatically, without us having to
juggle `-isystem, -I, -L -l, -rpath, -rpath-link` in an infinite dance.

Also note that the compiler is configured with: `-march=armv6`. Which is what is
actually missing in the upstream debian pre-packaged cross-compilers.

# How to figure out the versions of libc on a given platform

```bash

GCC_FEATURES=$(gcc -dM -E - <<< "#include <features.h>")

if grep -q __UCLIBC__ <<< "${GCC_FEATURES}"; then
    echo "uClibc"
    grep "#define __UCLIBC_MAJOR__" <<< "${GCC_FEATURES}"
    grep "#define __UCLIBC_MINOR__" <<< "${GCC_FEATURES}"
    grep "#define __UCLIBC_SUBLEVEL__" <<< "${GCC_FEATURES}"
elif grep -q __GLIBC__ <<< "${GCC_FEATURES}"; then
    echo "glibc"
    grep "#define __GLIBC__" <<< "${GCC_FEATURES}"
    grep "#define __GLIBC_MINOR__" <<< "${GCC_FEATURES}"
else
    echo "something else"
fi
```

Which will give you something like:

```
#define __GLIBC__ 2
#define __GLIBC_MINOR__ 28
```

Also check the libstcxx version:

```bash
glibccpberrypi:~$ strings /usr/lib/arm-linux-gnueabihf/libstdc++.so.6 | grep -i
GLIBCXX_3.4
GLIBCXX_3.4.1
GLIBCXX_3.4.2
GLIBCXX_3.4.3
GLIBCXX_3.4.4
GLIBCXX_3.4.5
GLIBCXX_3.4.6
GLIBCXX_3.4.7
GLIBCXX_3.4.8
GLIBCXX_3.4.9
GLIBCXX_3.4.10
GLIBCXX_3.4.11
GLIBCXX_3.4.12
GLIBCXX_3.4.13
GLIBCXX_3.4.14
GLIBCXX_3.4.15
GLIBCXX_3.4.16
GLIBCXX_3.4.17
GLIBCXX_3.4.18
GLIBCXX_3.4.19
GLIBCXX_3.4.20
GLIBCXX_3.4.21
GLIBCXX_3.4.22
GLIBCXX_3.4.23
GLIBCXX_3.4.24
GLIBCXX_3.4.25
GLIBC_2.4
GLIBC_2.18
GLIBC_2.16
GLIBC_2.17
GLIBCXX_DEBUG_MESSAGE_LENGTH
pi@raspberrypi:~$
```

Note that `libstcxx` links to `libc`.


[1]

The rule of cross compilation (and you have probably heard this before), is _do_
match libc versions (For C++ this also applies to libstdcxx). This is because
libc symbols are versioned, and since we are downloading packages, and linking
to packages already existing on the raspberry pi's, we are forced to use the
same version of the toolchain that they are using.


