# Secure Software & Hacking: Course Project
In this project, you will attack a remote HTTP server application and launch a keylogger on the remote machine to capture all keyboard input.
You must analyze and reverse engineer the vulnerable server application, discover exploitable bugs, and create exploits for different server and mitigation configurations.
Even though we intentionally inserted vulnerabilities in this server application, you will notice that you require enough knowledge about the lower levels of the software stack (see the course lectures, and the courses on Operating Systems and Intro to Computer Architecture), familiarity with some tools (see the lab sessions), and some creativity to build working exploits.

You have to work in groups of two students.
Each group gets a Gitlab repo to collaborate and to submit their final work.
You have to give us a short progress update during the second lab session and an oral presentation of your work at the end of the semester.

If you have questions, you can find Alicia Andries and Ruben Mechelinck in office G216 or during the lab sessions.
Make sure you read this assignment thoroughly **before** asking questions.

**Important requirement**: you need an x86-64 machine for this project.
We can host a limited number of VMs for groups in which no member has an x86-64 machine.


## Introduction: Architectural Overview
There are two different machines in play:
* The **remote machine** runs the vulnerable server application.
This is the machine you (i.e., the attacker) must attack and install the keylogger on.
You cannot log into this machine or inspect system resources (e.g., memory, files, or process information).
You can only interact over the network with the victim HTTP server itself.
* The **attacker machine** is the one on which you perform your offline program analyses and build and test your exploits.
Here, you have complete control over the execution environment and can inspect system resources.
You can freely use any analysis tools to examine the victim binary image.
You could, for example, run static analysis tools such as disassemblers/decompilers or dynamic analysis tools such as debuggers, fuzzers, and tracers.
For the latter, you should try to faithfully recreate the remote machine's environment (i.e., use the OS, kernel, libc version, etc.) to ensure that you can reproduce the execution of your exploits on the remote machine.
Note: in a realistic attack setting, an attacker often does not have the (exact same) binary image and might not know every detail about the victim's execution environment.
When the final exploit is ready, the attacker launches it to attack the victim server on the remote machine.


## Assignment
Below, you find a table that describes different scenarios. Each one presents you with a different server configuration and applied mitigations.
Your assignment is to build one exploit per scenario for as many scenarios as possible.
Each exploit should launch a keylogger on the remote machine and allow you to read the logged keyboard events.
We have given you access to a copy of the victim server binary image for each scenario.
You can perform your offline analyses and build your exploits using those copies. We also provide a minimal working keylogger implementation written in Rust.
You will have to tailor this implementation to the needs of your exploits.

You will have to **find (enough) exploitable bugs** before you can build a functional exploit.
You can analyze the given server binaries with any technique or tool you want (disassembling, decompiling, debugging, running with sanitizers, etc.).
**Advice:** do not start randomly analyzing the whole binary to discover bugs.
We only inserted a limited number of intentional bugs, so you could waste time running full-program analyses.
Instead, figure out the coarse structure of the code first, and think about what you want to accomplish with your exploit and what steps it involves.
Then, look for relevant pieces in the code and check if those contain any bugs.
The bugs you should look for are **stack buffer overwrites and overreads, uses of uninitialized memory, logic errors, and heap use-after-frees**.

If you get stuck during the development of (a part of) an exploit for a particular scenario, we will allow you to take some **minor shortcuts** in exchange for a reduced score.
For example, we could allow you to install the file manually if you need to create a file on the remote machine but cannot find a way to do it within your exploit.
You cannot, however, deactivate any of the mitigations since we do not consider this a minor shortcut.
If you are unsure whether some action constitutes an acceptable shortcut, please contact Ruben and Alicia to discuss your plans.


### Intermediate Progress Update
As a first step, you have to reverse engineer the **`log_message`** function by manually disassembling it, writing down its functionality in (pseudo) C, and drawing its stack layout.
Keep an eye open for any bug you discover here (hint).
We give you an example of the **`build_200_reponse_read`** function.
You should be able to do this assignment after the first lab session.

During lab 2, every group privately gives us a concise progress update where you show us:
* Your results of the above exercise.
* Any other progress you made. This could include:
    * An overview of the discovered bugs or irregularities and how you found them.
    * A description of your initial attempts to build exploits.

Your progress update will contribute to your overall grade.
At the end of the lab session, we will guide you through building one exploit for scenario 1.

### Final Presentation & Submission
At the end of the semester, you have to submit everything in the **`main` branch** of your given Gitlab repo.
For each scenario you looked at, you must include a separate script (e.g., in bash or python) that performs your attack automatically (see the one we built for scenario 1 during the lab).
We propose the following directory layout:

```shell
├── repo_root
│   ├── README.md          # global readme
│   ├── scenario_1         # subdirectory with everything for need for scenario 1
│   │   ├── keylogger      # the keylogger source used for this scenario. You do not have to duplicate the same source code for different scenarios. Instead, you can simply describe which source code you (re)used in the README.md file you write for each scenario.
│   │   │   ├── Cargo.toml
│   │   │   └── src
│   │   │       └── main.rs
│   │   ├── scenario_1.sh  # a script that automatically launches the attack. Make sure **you explain every step** in the script with comments: what does each command do, what does each hex string represent, etc.
│   │   └── README.md      # a file that contains info about which bugs you exploited, how you found them, whether there are missing parts in your exploit, which shortcuts you took to get to a working exploit. You should also include clear instructions on how to launch your attack script.
│   ├── scenario_2
│   │   └── ...
│   └── ...
```

In the same week, each group will orally present to us:
* All bugs you discovered, how you found them, and whether you exploited them in one of your exploits.
* The exploits you wrote. If some exploits are incomplete or only work after installing shortcuts, you can present the working parts and outline which parts are missing.
* Any changes you made to the keylogger to facilitate your exploits.
* A live demonstration of the working exploits. For this demo, you must connect to our private network over Ethernet and attack a remote server.
* Your thoughts on possible code patches or existing system-level protections or mitigations that eliminate your exploits.
Afterwards, we will ask you some questions.


## Attack Scenarios
The table below shows the scenarios for which you must build different exploits.
They are ordered approximately by difficulty level, but you are not obligated to follow this order.
In contrast to the lab sessions about finding bugs and writing exploits, in these scenarios, you will stumble upon additional obstacles that you need to overcome with some creativity.
You can build an exploit for each scenario with only one or two exploitable bugs at its core.

| no. | `server_data` access¹ | stack canary | DEP² | ASLR³ | comments |
| :-: | :-------------------: | :----------: | :--: | :---: | -------- |
| 1   | accessible            | no           | no   | no    | you can copy your keylogger binary directly into `server_data` and read its output there as well |
| 2   | accessible            | no           | yes  | no    | no additional bugs required compared to scenario 1 |
| 3   | not accessible        | no           | no   | no    | like scenario 1 but with 2 new challenges: 1. installing your executable keylogger binary on the remote machine, 2. sending output back to the attacker |
| 4   | accessible            | no           | yes  | yes   | this requires a successful exploit for scenario 2 first |
| 5   | accessible            | yes          | no   | no    | do not try to change a return address, look for other indirect (forward) edges |
| 6   | not accessible        | yes          | yes  | yes   | have a look at the ELF .dynamic section and think about function interposition |

¹ when accessible, you can read and write in the directory without going through the server application.\
² Data Execution Prevention (aka W⊕X)\
³ Address Space Layout Randomization (with PIE)


## Getting Started
### Repo Structure
This repo's root directory contains:
* The `keylogger` directory with a minimal working keylogger implementation.
* The `examples` directory with a disassembly of the `log_message` function you should reverse engineer, along with an example implementation of the `build_200_response_read` function.
* The `server` directory with:
    * The `launch_scenario` program.
    This program will set up the scenario parameters, start the server, and restart it whenever it crashes (more info below).
    * The server binaries, one for each scenario: `server_sc<scenario_id>`.
    These are the binaries you, the attacker, have access to for analysis on the attacker machine.
    The source code for the different scenarios is **almost** identical.
    For some scenarios, however, it may contain one or two minor tweaks, so be sure to **re-validate your assumptions** whenever you start on a new scenario!
    For scenarios 4 and 5, you also get a server binary compiled with address sanitizer (ASAN).
    * `server.h` is the header file of the server application. This file contains all declarations with some minor comments.
    * The `server_data` directory which contains all data files used by the server application: `home.html`, `data.txt`, and the stats program.
    You can assume these files are always present when the server launches.

### Project Setup
You must run the attacker and remote machines in a Virtual Machine (VM).
We opted to use VMs for this assignment since they provide isolation from your host machine.
Running the machines in a Docker will not suffice since these containers still use the host's kernel and the host's `/dev`, `/sys`, `/proc`, etc. directories, into which we need to read or write to accommodate the different scenarios.

Download one of [these](https://www.osboxes.org/debian/#debian-11-vbox) prepackaged **Debian 11 Server 64 bit** VM images for VirtualBox or VMWare.
I repeat, **Debian**, version **11**, **64 bit**, the **Server** image!
These images do not require many resources (256 MiB memory is sufficient for the remote machine VM), so you could create two instances to represent the attacker and remote machine and run them both simultaneously.
Then, follow the setup instructions below.
You could also run both machines in the same VM instance, **but you must ensure your final exploits do not require any changes to the execution environment**.
Before submitting, ensure your exploits work in a clean, out-of-the-box VM.
The remote server we will provide for your demo will run in a clean Debian 11 Server 64 bit VM.

To get started, you should launch the VM(s) in headless mode and SSH into them whenever you want to run anything on the attacker or remote machines.
When using the *NAT* network adapter, you will have to set up port forwarding in your VM hypervisor (for [VirtualBox](https://www.simplified.guide/virtualbox/port-forwarding) or [VMWare](https://www.virten.net/2013/03/how-to-setup-port-forwarding-in-vmware-workstation-9/)) to forward port 22 (= SSH default port) of the VM to an accessible port (e.g., 2222) on the host.
This way, you can SSH into the VM with `ssh osboxes@localhost -p 2222`. You might do the same for port 8080 to access the server application from the host or the second VM.

Then, inside the VM, you should run
```shell
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get dist-upgrade
$ git clone https://github.com/ku-leuven-msec/secure-software-and-hacking-assignment
```

**Note**: if you do want to use two separate VMs:
* On VirtualBox, you will have to regenerate the UUID of the second VDI file.
Use `VBoxManage internalcommands sethduuid <filename>.vdi`.
* Use a different host port in the SSH port forwarding of the second VM.
* When using the *NAT* network adapter, two VMs can communicate with each other **through the host**, using the host IP address and the port assigned to the receiving VM.
* Note: the *Bridged* network adapter **will not work on campus** because the campus network does not give more than one IP address per network adapter.

### The Server Application
**Read this section thoroughly!** You need to know how the server operates before you can exploit it.
#### Operations
The server accepts HTTP GET, POST, and PUT requests that interact with files in the `server_data` directory:
* GET sends the specified file to the client.
* POST appends the HTTP body to the specified file.
It returns 404 if the specified file does not exist.
* PUT creates the specified file and fills it with the HTTP body.
The server overwrites the file if it already exists.

All file operations are restricted to the `server_data` directory.
Do not try to escape this directory.

The PUT request requires authentication using [HTTP Basic Authentication](https://en.wikipedia.org/wiki/Basic_access_authentication).
It decodes the provided base64 credentials, hashes the password (SHA256, without salt), and checks its validity. There is only one authenticated user and password pair.
You cannot intercept an interaction between the server and an actor that knows the password.
You should also (obviously) not try to reverse the hashed password.
In other words, do not waste time trying to get the plaintext password.

When reading the request, the server first reads the whole header (**ending with "\r\n\r\n"**), parses it, extracts the "Content-Length" field, and then reads the entire body based on the content length.
If your request does not contain the header ending or has a "Content-Length" field larger than its body, the server will wait for the client to send more data until the client closes the connection.
The "Content-Length" field is optional for GET requests. Be sure to experiment with this blocking behavior.

#### Launching
Use the `launch_scenario` program to set up the scenario automatically. For example:
```shell
$ sudo ./launch_scenario 1
$ sudo ./launch_scenario 4_asan
```
These programs set the required system parameters, restore the contents of the files in `server_data`, remove the log file, and start the server application.
The programs also automatically restart the server application whenever it terminates with an error.
You can rely on this behavior in your exploits.
On the demo machine we will use at the end of the semester, we will also launch the server using the `launch_scenario` program.
You may assume the running server instance you attack is not widely used by other actors and runs idle most of the time.

#### Info
The vulnerable HTTP server application is written in C, runs with root privileges on a Linux host, and accepts connections on port 8080.
The server spawns a **new thread with a thread-local stack for each incoming connection**.
We compiled the server into x86_64 ELF binaries without debug symbols for all scenarios.
We used clang 11.0.1 as the compiler and compiled with optimization flags that include `-O1 -fno-omit-frame-pointer`.
The `server.h` file contains a list of functions without (intentional) bugs.


## Useful Links & Info
* Documentation about Linux tools and libc functions: https://www.man7.org/linux/man-pages/ (or use the `man <tool-or-function-name>` command)
* x86 opcode documentation: https://www.felixcloutier.com/x86/
* x86-64 system call numbers and arguments: http://blog.rchapman.org/posts/Linux_System_Call_Table_for_x86_64/
* (7 bit) ASCII table: https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/ASCII-Table-wide.svg/1280px-ASCII-Table-wide.svg.png
* Online (dis)assembler with hexadecimal representation: https://defuse.ca/online-x86-assembler.htm
* https://gcc.gnu.org/onlinedocs/gcc/Return-Address.html
* https://www.man7.org/conf/lca2006/shared_libraries/slide19a.html

Some info about the `execve` system call:
* The argv and envp each point to an **array** of char **pointers**.
Those char pointers point to (null-terminated) **strings**.
Do not try to use these pointers to point to any type other than strings!
* The argv and envp arrays are both terminated with a NULL pointer (= 8 bytes!).

On x86:
* The stack grows from higher to lower addresses (with `push` and `pop`).
However, data on the stack is read and written from lower to higher addresses.
* The stack pointer (`rsp`) always points to the last pushed item.
* Data types that consist of multiple bytes are stored in little-endian format in memory.

Others:
* The heap is not executable by default on modern Linux versions, even with DEP turned off.


## Useful Tools
* Send HTTP request using `curl`
```shell
$ curl --request POST '127.0.0.1:8080/data.txt' --header 'Content-Type: text/plain' --header 'Authorization: Basic dXNlcjpwYXNz' --data 'some data'
```

* With `curl`, you do not have fine control over how exactly the HTTP request will look because `curl` adds extra information in the HTTP header.
If you need fine control over the request, use netcat:
```shell
$ nc localhost 8080 < request.http
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
Alternatively, without using a file:
```shell
$ echo -n -e "GET /data.txt HTTP/1.1\r\nContent-Type: text/plain\r\nContent-Length: 9\r\n\r\nsome data" | nc localhost 8080
```

* To get the exact file length in bytes:
```shell
$ wc -c < path/to/file
```

* Assemble assembly code to binary code
```shell
$ nasm /path/to/input_file -o /path/to/output_file
```

* Disassemble binary code to assembly code
```shell
$ objdump -d -M intel /path/to/input_file > /path/to/output_file
```

* To convert bytes (for example, bytes of an ASCII string) from a file or standard input to hexadecimal form:
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

* When you need the size of a type, and the documentation does not specify this, you can get it programmatically using a simple C program. For example, for the `sockaddr_in` struct:
```C
#include <stdio.h>
#include <netinet/in.h>

int main() {
    printf("%lu\n", sizeof(struct sockaddr_in));
    return 0;
}
```

* Use `readelf` to inspect ELF specific metadata like headers, tables, etc.

* To debug the server started with `launch_scenario` with GDB. The server prints its process ID at startup.
```shell
$ sudo gdb -tui -p <pid>
```
**Note**: do not start `launch_scenario` with GDB.

* Some useful options in `~/.gdbinit`
```
set disassembly-flavor intel
```


