update:
	#!/bin/bash
	git pull
	git submodule update --init --recursive --remote

build:
	#!/bin/bash
	cmake -S . -B build
	cmake --build build
	python3 common/pack_meta.py build/app.bin -m package.json -o build/app.mbin

disasm: build
	#!/bin/bash
	cmake --build build --target disasm

clean:
	#!/bin/bash
	rm -rf build
