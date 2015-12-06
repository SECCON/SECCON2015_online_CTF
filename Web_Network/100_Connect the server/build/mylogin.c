#include <stdio.h>
#include <unistd.h>

void flag(FILE *fpw)
{
	const char *the_flag = "But you can get the FLAG: SECCON{Sometimes_what_you_see_is_NOT_what_you_get}";
	const char *p;

	for (p = the_flag; *p; p++) {
		fputc(*p, fpw);
		fputc('\b', fpw);
		fputc(' ', fpw);
		fputc('\b', fpw);
	}
}

//#define BPS 1200
#define BPS 300
//#define BPS 75
//#define BPS 0

void show(FILE *fpw, const char *msg)
{
	const char *p;
	for (p = msg; *p; p++) {
		if (*p == '\n') fputc('\r', fpw);
		fputc(*p, fpw);
		fflush(fpw);
		if (BPS > 0) usleep(1000*1000*10/BPS);
	}
}

void discard_input(FILE *fpr)
{
	int fd = fileno(fpr);
	fd_set readfds;
	struct timeval tv;

	FD_ZERO(&readfds);
	FD_SET(fd, &readfds);
	tv.tv_sec = 0;
	tv.tv_usec = 0;
	while (select(FD_SETSIZE, &readfds, NULL, NULL, &tv) > 0) {
		char buf[1024];
		ssize_t len;

		if ((len = read(fd, buf, sizeof(buf))) < 0) break;
	}
}

int main()
{
	int ch;
	FILE *fpr = stdin;
	FILE *fpw = stdout;

	sleep(1);

	printf("CONNECT");
#if BPS > 0
	printf(" %u", BPS);
#endif
	printf("\r\n");
	fflush(stdout);

	sleep(1);

	show(fpw, "\nWelcome to SECCON server.\n");

	int name_ok = 0;

	while (!name_ok) {
		show(fpw, "\nlogin: ");
		discard_input(fpr);

		while ((ch = getchar()) != EOF) {
			if (ch == '\n') break;
			if (ch == '\r') continue;

			name_ok = 1;
		}
		if (ch == EOF) break;
		sleep(1);
	}

	show(fpw, "\n");
	if (ch != EOF) {
		show(fpw, "Sorry, the server is currently unavailable.\n");
		flag(fpw);
	}
	show(fpw, "\nGood bye.\n");

	sleep(1);

	return 0;
}
