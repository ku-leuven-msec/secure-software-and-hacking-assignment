#include <netinet/in.h>

//This code follows the same structure as the disassembly code
//Note: the code in L2 is duplicated to recreate stuctured control flow

int log_message(const char* message, ssize_t message_len, int* client_fd) {
    int ret;
    char s[1024];
    char dst[16];
    struct sockaddr addr;
    size_t addr_len = 16; // = sizeof(struct sockaddr);
    ret = -1;

    if (!getsockname(*client_fd, &addr, &addr_len)) {
        //When 1st arg is AF_INET: 2nd arg is pointer to `struct in_addr` (https://man7.org/linux/man-pages/man3/inet_ntop.3.html) => implies cast to specialized type `sockaddr_in` (https://www.man7.org/linux/man-pages/man3/sockaddr.3type.html)
        if (inet_ntop(AF_INET, &((struct sockaddr_in)addr).sin_addr, dst, 16)) {
            ret = 0;
            memset(s, 0, 1024);
            sprintf(s, "== Request from %-15s at fd %-10d\n%s", dst, *client_fd, message);
            puts(s);
            FILE* file = fopen("../server.log", "a");
            if (file) {
                fprintf(file, "%s\n\n", s);
                char* stats = malloc(4096);
                get_server_stats(stats, 4096);
                fprintf(file, "%s\n\n", stats);
                free(stats);
                fclose(file);
            } else ret = -1; //L2
        } else ret = -1; //L2
    }
//L1
}