## Useful Links & Info
* Documentation about Linux tools and libc functions: https://www.man7.org/linux/man-pages/ (or use the `man <tool-or-function-name>` command)
* x86 opcode documentation: https://www.felixcloutier.com/x86/
* x86-64 system call numbers and arguments: http://blog.rchapman.org/posts/Linux_System_Call_Table_for_x86_64/
* (7 bit) ASCII table: https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/ASCII-Table-wide.svg/1280px-ASCII-Table-wide.svg.png
* Online (dis)assembler with hexadecimal representation: https://defuse.ca/online-x86-assembler.htm
* Useful for scenario 6: https://gcc.gnu.org/onlinedocs/gcc/Return-Address.html and https://www.man7.org/conf/lca2006/shared_libraries/slide19a.html

In the `execve` system call, the `argv` and `envp` arguments each point to an **array** of char **pointers**.
Those char pointers point to null-terminated (\0) **strings**.
The array is terminated with a (64 bit) NULL pointer.
Do not try to use these pointers to point to any type other than strings!

On x86:
* The stack grows from higher to lower addresses.
However, data on the stack is read and written from lower to higher addresses.
* The stack pointer (`rsp`) always points to the last pushed item.
* Data types that consist of multiple bytes are stored in little-endian format in memory.

Others:
* The heap is not executable by default on modern Linux versions, even with DEP turned off.
* **When ASLR is disabled**, you can leverage the know location of the code section in memory and the rough location of the stack to recognize pointers in memory dumps.
For example, pointers into the code section will look like `0x40XXXX`, while pointer into the stack usually look like `0x7FFFFXXXXXXX`.


## Useful Tools
* Send HTTP request using `curl`:
    ```shell
    $ curl --request POST '<HOST_IP>:8080/data.txt' --header 'Content-Type: text/plain' --header 'Authorization: Basic dXNlcjpwYXNz' --data 'some data'
    ```

* With `curl`, you do not have fine control over how exactly the HTTP request will look like because `curl` adds extra information in the HTTP header.
If you need fine control over the request, use netcat:
    ```shell
    $ nc <HOST_IP> 8080 < request.http
    ```
    with `request.http`:
    ```http
    PUT /data.txt HTTP/1.1
    Content-Type: text/plain
    Authorization: Basic dXNlcjpwYXNz
    Content-Length: 9

    some data
    ```
    Note that, according to the HTTP standard, every new line is a "\r\n"!
    Alternatively, without using a request file:
    ```shell
    $ echo -n -e "GET /data.txt HTTP/1.1\r\nContent-Type: text/plain\r\nContent-Length: 9\r\n\r\nsome data" | nc <HOST_IP> 8080
    ```

* To get the exact file length in bytes:
    ```shell
    $ wc -c < path/to/file
    ```

* Assemble assembly code to binary code:
    ```shell
    $ nasm /path/to/input_file -o /path/to/output_file
    ```

* Disassemble binary code to assembly code:
    ```shell
    $ objdump -d -M intel /path/to/input_file > /path/to/output_file
    ```

* To convert bytes (for example, bytes of an ASCII string) to hexadecimal form:
    ```shell
    $ xxd /path/to/file                #formated output
    $ xxd -p /path/to/file             #raw
    $ xxd -p -r /path/to/file          #reverse: hex -> bytes
    $ xxd -p /path/to/file | xxd -p -r #bytes -> hex -> bytes
    ```

* Append backslash escape characters to a file ("\x60" = 0x60):
    ```shell
    $ echo -n -e "\x60\xf1\n\t\x00\x7f" >> path/to/file
    ```

* <a id="structs"></a> When you need the size of a type or the offsets of its fields, and the documentation does not specify this, you can get it programmatically using a simple C program. For example, for the `sockaddr_in` struct:
    ```C
    #include <stdio.h>
    #include <stdint.h>
    #include <netinet/in.h>

    int main() {
        struct sockaddr_in instance;
        printf("struct size: %lu\n", sizeof(struct sockaddr_in));
        printf("offset of 'sin_port' field: %lu\n", (uintptr_t)&instance.sin_port - (uintptr_t)&instance);
        return 0;
    }
    ```

* Use `readelf` to inspect ELF specific metadata like headers, tables, etc.

* To debug the server with GDB when started with `launch_scenario`:
    ```shell
    $ gdb -tui -p <pid>
    ```
    **Notes:**
    * The server prints its process ID at startup.
    * Do not start `launch_scenario` with GDB!

* Some GDB options:
    * Useful options to put in `~/.gdbinit`: `set disassembly-flavor intel`




