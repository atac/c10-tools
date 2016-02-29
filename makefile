
all:
	for file in c10-*.py; do \
		pyinstaller -F $$file -p ../pychapter10 --exclude-module matplotlib; \
	done
	pyinstaller -F pcap2c10.py -p ../pychapter10 --exclude-module matplotlib

clean:
	rm -rf dist build *.spec

install:
	cp dist/* ~/bin
