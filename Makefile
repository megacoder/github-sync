TARGETS=all check clean clobber distclean install uninstall
TARGET=all

PREFIX=${DESTDIR}/opt
BINDIR=${PREFIX}/bin
SUBDIRS=

ifeq	(${MAKE},gmake)
	INSTALL=ginstall
else
	INSTALL=install
endif

.PHONY: ${TARGETS} ${SUBDIRS}

all::	github-sync.py

${TARGETS}::

clobber distclean:: clean

check::	github-sync.py
	./github-sync.py ${ARGS}

install:: github-sync.py
	${INSTALL} -D github-sync.py ${BINDIR}/github-sync

uninstall::
	${RM} ${BINDIR}/github-sync

ifneq	(,${SUBDIRS})
${TARGETS}::
	${MAKE} TARGET=$@ ${SUBDIRS}
${SUBDIRS}::
	${MAKE} -C $@ ${TARGET}
endif
