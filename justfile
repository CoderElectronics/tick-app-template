update:
	#!/bin/bash
	git pull
	git submodule update --init --recursive --remote

build:
	#!/bin/bash
	cmake -S . -B build
	cmake --build build

disasm: build
	#!/bin/bash
	cmake --build build --target disasm

clean:
	#!/bin/bash
	rm -rf build
