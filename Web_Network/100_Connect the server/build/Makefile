all: mylogin

mylogin: mylogin.c
	cc -o mylogin mylogin.c

run:
	socat tcp4-listen:10000,fork,reuseaddr,nodelay exec:./mylogin

clean:
	rm -f mylogin
