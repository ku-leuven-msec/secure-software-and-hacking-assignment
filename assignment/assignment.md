## Assignment
Below, you find a table that describes different scenarios. Each one presents you with a different server configuration and applied mitigations.
Your assignment is to build one exploit per scenario for as many scenarios as possible.
Each exploit should launch a keylogger on the remote victim machine and allow you to read the logged keyboard events.

You have access to a copy of the vulnerable server binary image for each scenario.
Before you can build a functional exploit, you have to **find (enough) exploitable bugs** in the given victim binaries.
You can analyze them with any technique or tool you want (disassembling, decompiling, debugging, running with sanitizers, etc.).
**Advice:** do not start randomly analyzing the whole binary to discover bugs.
We only inserted a limited number of intentional bugs, so running full-program analyses will waste a lot of time.
Instead, figure out the coarse structure of the code first (be sure to look at `server.h`!), and think about what you want to accomplish with your exploit and what steps it involves.
Then, look for relevant pieces in the code and check if those contain any bugs.
A scenario could be exploited in multiple ways.
For some scenarios, we provide a version compiled with address sanitizer (ASAN).
Be sure to use those to find bugs by constructing inputs that trigger an ASAN exception.
The bugs you should look for are **stack buffer overwrites and overreads, uses of uninitialized memory, logic errors, format string errors and heap use-after-frees**.

We also provide a minimal working keylogger implementation written in Rust.
You will have to tailor this implementation to the needs of your exploits.

If you get stuck during the development of (a part of) an exploit for a particular scenario, we will allow you to take some **minor shortcuts** in exchange for a reduced score.
For example, we could allow you to install the file manually if you need to create a file on the victim machine but cannot find a way to do it within your exploit.
You cannot, however, deactivate any of the mitigations since we do not consider this a minor shortcut.
If you are unsure whether some action constitutes an acceptable shortcut, please contact Ruben and Alicia to discuss your plans.

### Intermediate Progress Update
As a first step, you have to reverse engineer the **`log_header`** function by manually disassembling it, writing down its functionality in (pseudo) C, and drawing its stack layout.
You should read and understand the assembly code and look at the stack operations to figure out the layout of the data on the stack.
All stack operations are performed using register-indirect addressing with `rbp`.
Also, have a look at [this](tools_and_info.md#structs).
Keep an eye open for any bug you discover in this function (hint).
We give you an example of the **`build_200_reponse_read`** function.
You can find all required files in the `examples` directory.
You should be able to do this assignment after the first lab session.

During lab 2 (28 Februari), every group privately gives us a concise progress update where you discuss:
* Your results of the above exercise.
* Any other progress you made.
This could include:
    * An overview of the discovered bugs or irregularities and how you found them.
    * A description of your initial attempts to build exploits.
Make sure to push your solution to your Gitlab repo (see repo structure below).

If you cannot be present during this lab session, please contact Ruben and Alicia to arrange a different time slot.
Your progress update will contribute to your overall grade.
The most important part is your stack representation so make sure it is precise and contains enough details (see the example)!!
Afterwards, we will upload the solution and an example exploit for scenario 1.

During the second half of lab 4 (28 March), you can work on your project and ask questions or feedback about your exploit approaches.

### Final Presentation & Submission
At the end of the semester, you have to submit everything in the **`main` branch** of your given Gitlab repo.
For each scenario you looked at, you must include a separate script (e.g., in bash or python) that performs your attack automatically (see the example for scenario 1 given later).
We propose the following directory layout:

```shell
├── repo_root
│   ├── README.md          # a file containing info about every scenario you exploited: the course operations of your exploit, which bugs you exploited, how you found them, the payload structure (if there is one) whether there are missing parts in your exploit, which shortcuts you took to get to a working exploit. You should also include clear instructions on how to launch your attack script for each scenario.
│   ├── progress_update    # your solution for the intermediate progress update
│   │   ├── log_header__stack.pdf
│   │   ├── log_header__pseudo.c
│   │   ├── log_header__disassembly.txt
│   ├── scenario_1         # subdirectory with everything for need for scenario 1
│   │   ├── keylogger      # the keylogger source used for this scenario. You do not have to duplicate the same source code for different scenarios. Instead, simply describe which source code you reused in the README.md file.
│   │   │   ├── Cargo.toml
│   │   │   └── src
│   │   │       └── main.rs
│   │   ├── scenario_1.py  # a script that automatically launches the attack. Make sure **you explain every step** in the script with comments: what does each command do, what does each hex string represent, etc.
│   ├── scenario_2
│   │   └── ...
│   └── ...
```

In the same week, each group will orally present to us:
* All bugs you discovered, how you found them, and whether you exploited them in one of your exploits.
* The exploits you wrote.
If some exploits are incomplete or only work after installing shortcuts, you can present the working parts and outline which parts are missing.
* Any changes you made to the keylogger to facilitate your exploits.
* A live demonstration of the working exploits on your own setup.
We may ask you to gradually step through your exploit or attach GDB to the server and give us extra information about what is happening internally.
* Your thoughts on possible code patches or existing system-level protections or mitigations that eliminate your exploits.
Afterwards, we will ask you some questions.


## Attack Scenarios
The table below shows the scenarios for which you must build different exploits.
They are ordered approximately by difficulty level, but you are not obligated to follow this order.
In contrast to the lab sessions about finding bugs and writing exploits, in these scenarios, you will stumble upon additional obstacles that you need to overcome with some creativity.
You can build an exploit for each scenario with only one or two exploitable bugs at its core and you can usually reuse parts across the different exploits.
Your exploit is successful when the keylogger is executing on the remote victim machine and the attacker can read its output from the attacker machine.
You do not have to preserve the functionality of the server application after a successful attack.

| no. | `server_data` access¹ | stack canary | DEP² | ASLR³ | comments |
| :-: | :-------------------: | :----------: | :--: | :---: | -------- |
| *Basic* |
| 1   | accessible            | no           | no   | no    | you can copy your keylogger binary directly into `server_data` and read its output there as well |
| 2   | accessible            | no           | yes  | no    | no additional bugs required compared to scenario 1 |
| 3   | not accessible        | no           | no   | no    | like scenario 1 but with two new challenges: 1. installing your executable keylogger binary on the victim machine, 2. sending output back to the attacker |
| 4   | accessible            | no           | yes  | yes   | this requires a successful exploit for scenario 2 first |
| *Advanced* |
| 5   | not accessible        | no           | yes  | yes, without PIE⁴ | similar challenges to 3 but harder to overcome, TIP: bypass the authentication |
| 6   | not accessible        | yes          | yes  | yes   | have a look at the ELF `.dynamic` section (e,g,. using `readelf`) and think about function interposition |
| 7   | not accessible        | no           | yes  | yes, without PIE⁴ | similar to 5 but SELinux prevents executable files in `server_data`, TIP: escape the `server_data` directory |

¹ When accessible, you can copy the keylogger binary to the `server_data` directory and read the existing files it contains, without going through the server application.
For example, using `scp -P <PORT> path/to/keylogger student@<IP_ADDRESS>:/home/student/server/server_data`.
You are NOT allowed to change or overwrite any existing files.
You still need to create an exploit for the server application to launch the keylogger.\
² Data Execution Prevention (aka W⊕X, aka NX).\
³ Address Space Layout Randomization and the server binary is a Position Independent Executable (PIE).\
⁴ The base addresses of the stack, heap, and shared libaries are randomized but the base address of the server code is **not** randomized.



