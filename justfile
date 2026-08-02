update:
	#!/bin/bash
	git pull
	git submodule update --init --recursive --remote

build:
	#!/bin/bash
	make

clean:
	#!/bin/bash
	make clean
