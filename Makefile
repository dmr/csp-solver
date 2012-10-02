minisat:
	git clone https://github.com/niklasso/minisat.git
	cd minisat && make config prefix=.
	cd minisat && make
	cd minisat && make install
	mkdir -p ~/bin
	env
	cp minisat/bin/minisat ~/bin/
