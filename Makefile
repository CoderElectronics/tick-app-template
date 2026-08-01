TOPDIR=./
PROJECT=app
SRCS=src/main.c common/crt0.S

all: all_template
test: test_template
clean: clean_template

include common/makefile.template
