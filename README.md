# Secure Software & Hacking: Course Project
In this project, you will attack a remote HTTP server application and launch a keylogger on the remote victim machine to capture all keyboard input.
You must analyze and reverse engineer the vulnerable server application, discover exploitable bugs, and create exploits for different server and mitigation configurations.
Even though we intentionally inserted vulnerabilities in the server application, you will notice that you require enough knowledge about the lower levels of the software stack (see the course lectures, and the courses on Operating Systems and Intro to Computer Architecture), familiarity with some tools (see the lab sessions), and some creativity to build working exploits.

You have to work in groups of two students.
Each group gets a Gitlab repo to collaborate and to submit their final work.
You have to give us a short progress update during the second lab session and an oral presentation of your work at the end of the semester.

If you have questions, you can find Alicia Andries and Ruben Mechelinck in office G216 or during the lab sessions.
Make sure you read this assignment thoroughly **before** asking questions.

**Important requirement**: you need an x86-64 machine for this project.
We can host a limited number of VMs for groups in which no member has an x86-64 machine.


## Introduction: Architectural Overview
There are two different machines in play:
* The **remote victim machine** runs the vulnerable server application.
This is the machine you (i.e., the attacker) must attack and install the keylogger on.
You cannot log into this machine or inspect system resources (e.g., memory, files, or process information).
You can only interact over the network with the victim HTTP server that runs on this machine.
* The **attacker machine** is your working machine on which you perform offline program analyses and build, test, and launch your exploits.
Here, you have complete control over the execution environment and can inspect system resources.
You can freely use any analysis tools to examine the victim binary image.
You could, for example, run static analysis tools such as disassemblers/decompilers or dynamic analysis tools such as debuggers, fuzzers, and tracers.
For the latter, you should try to faithfully recreate the victim machine's environment (i.e., use same the OS, kernel, libc version, etc.) to ensure that you can reproduce the execution of your exploits later when you attack the remote victim machine.
Note: in a realistic attack setting, an attacker often does not have the (exact same) binary image and might not know every detail about the victim's execution environment.


## Getting Started
Read [the assignment](assignment/assignment.md) for more details.
See [the setup file](assignment/setup.md) to setup the environment, [the server_operations file](assignment/server_operations.md) to learn how the vulnerable server operates, and the [tools_and_info file](assignment/tools_and_info.md) for useful info and tools to communicate with the server application.

This repo's root directory contains:
* The `assignment` directory contains all markdown files for the assignment.
* The `keylogger` directory with a minimal working keylogger implementation.
* The `examples` directory with a disassembly of the `log_header` function you should reverse engineer, along with an example for the `build_200_response_read` function.
* The `server` directory (inside `server.tar.gz`) with:
    * The `launch_scenario` program.
    This program will set up the scenario, start the server, and restart it whenever it crashes (more info below).
    * The vulnerable server binaries, one for each scenario: `server_sc<SCENARIO_ID>`.
    These are the binaries you, the attacker, have access to for analysis on the attacker machine.
    The source code for the different scenarios is **almost** identical.
    For some scenarios, however, it may contain one or two minor tweaks, so be sure to **re-validate your assumptions** whenever you start on a new scenario!
    For scenarios 4 and 7, you also get a server binary compiled with address sanitizer (ASAN).
    * `server.h` is the header file of the server application.
    This file contains all declarations with some minor comments.
    It also list the functions with intentional bugs so be sure to have a look at it!!
    * The `server_data` directory containing all data files used by the server application: `home.html` and `data.txt`.
    You can assume these files are always present when the server launches.
