#include <stdio.h>
#include <unistd.h>
#include <time.h>

void flag(FILE *fpw)
{
	const char *the_flag = "SECCON{Sometimes_what_you_see_is_NOT_what_you_get}";
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

void discard_input(int fd)
{
	fd_set readfds;
	struct timeval tv;

	while (1) {
		FD_ZERO(&readfds);
		FD_SET(fd, &readfds);
		tv.tv_sec = 0;
		tv.tv_usec = 0;

		if (select(FD_SETSIZE, &readfds, NULL, NULL, &tv) > 0) {
			char buf[1024];
			ssize_t len;

			if ((len = read(fd, buf, sizeof(buf))) > 0) continue;
		}
		break;
	}
}

int readline_with_timeout(int fd, int t)
{
	fd_set readfds;
	struct timeval tv;
	int name_ok = 0;
	int ret;
	time_t start_t;

	start_t = time(NULL);

	while (1) {
		char ch;
		ssize_t len;

		FD_ZERO(&readfds);
		FD_SET(fd, &readfds);
		tv.tv_sec = 1;
		tv.tv_usec = 0;

		if ((ret = select(FD_SETSIZE, &readfds, NULL, NULL, &tv)) < 0) {
			// error
			return -1;
		}

		if (ret == 0) {
			if (start_t + t <= time(NULL)) {
				// timeout
				return 0 + name_ok;
			}
			continue;
		}

		if (read(fd, &ch, 1) <= 0) return -1; // EOF

		if (ch == 0x04) return -1;
		if (ch == '\r') continue;
		if (ch == '\n') return 2 + name_ok;

		name_ok = 1;
	}

	// error
	return -1;
}

int main()
{
	int ch;
	FILE *fpw = stdout;

	sleep(1);

	printf("CONNECT");
#if BPS > 0
	printf(" %u", BPS);
#endif
	printf("\r\n");
	fflush(stdout);

	sleep(1);

	show(fpw, "\n");
	show(fpw, "Welcome to SECCON server.\n");
	show(fpw, "\n");
	show(fpw, "The server is connected via slow dial-up connection.\n");
	show(fpw, "Please be patient, and do not brute-force.\n");
	flag(fpw);

	int bye = 0;
	int v;
	int count = 0;

	while (!bye) {
		show(fpw, "\n");
		show(fpw, "login: ");
		discard_input(STDIN_FILENO);

		switch ((v = readline_with_timeout(STDIN_FILENO, 20))) {
		case 0: // timeout
			show(fpw, "\n");
			show(fpw, "\n");
			show(fpw, "Login timer timed out.\n");
			show(fpw, "Thank you for your cooperation.\n");
			show(fpw, "\n");
			show(fpw, "HINT: It is already in your hands.\n");

			bye = 1;
			break;
		case 1: // timeout with name_ok
			show(fpw, "\n");
			show(fpw, "\n");
			show(fpw, "Login timer timed out.\n");

			bye = 1;
			break;

		case 2: // empty line
			sleep(1);
			continue;

		case 3: // name ok
			sleep(1);
			show(fpw, "\n");
			show(fpw, "Sorry, the account is unavailable.\n");
			bye = 1;
			break;

		default:
		case -1: // EOF
			show(fpw, "\n");
			bye = 1;
			break;
		}
	}

	show(fpw, "\n");
	show(fpw, "Good bye.\n");

	sleep(1);

	return 0;
}
