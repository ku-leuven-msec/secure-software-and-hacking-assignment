## VM Setup
You must run the attacker machine and remote victim machine in a Virtual Machine (VM).
We opted to use VMs for this assignment since they provide isolation from your host machine.
Running the machines in a Docker will not suffice since these containers still use the host's kernel and the host's `/dev`, `/sys`, `/proc`, etc. directories, into which we need to read or write to accommodate the different scenarios.

For the attacker machine, download the latest prepackaged [**64-bit Debian 12** VM image](https://www.osboxes.org/debian/) for **VirtualBox(!)**.
In VirtualBox, create a new VM called "attacker-machine" and, under "Hard Disk", select "Use an Existing Virtual Hard Disk File" to attach the disk image you just downloaded.
Install the guest additions if you want to share the clipboard or mount shared directories (select "Devices" -> "Insert Guest Additions CD Image", go to disk directory and run `sh ./autorun.sh`, reboot).
You have to use this VM for the lab exercises as well.
For the project however, if you run Linux natively, you can use your host instead of the VM as the attacker machine **only if your glibc version is 2.36 or lower (not higher!)** (check with: `ldd --version`).

For the victim machine, download [this](https://kuleuven-my.sharepoint.com/:u:/g/personal/ruben_mechelinck_kuleuven_be/EW3zoITv8m1FubnbaVkAMDEBums8t8Ej3jwcf71Sc9L8tQ?e=RLGIDN) Debian 12 disk image and create a new VM called "victim-machine".
This VM does not require many resources (256 MiB memory is sufficient) so you should be able to run it simultaneously with the attacker VM.

We advise you to use a *NAT* network adapter for both.
In this case, you will have to set up port forwarding in your VM hypervisor (for [VirtualBox](https://www.simplified.guide/virtualbox/port-forwarding)) to forward port 22 (= SSH default port) of the victim VM to an accessible port on the host (e.g., 2222).
This way, you can SSH into the victim VM from the attacker VM using `ssh student@<HOST_IP> -p 2222`, with HOST_IP being the IP address of your host(!) computer (not the VMs).
The server application uses port 8080, so you will have to set up another port forwarding for this port as well.

**Note**: the *Bridged* network adapter **will not work on campus** because the campus network does not give more than one IP address per network adapter.

To get started, launch both VMs.
Because the victim VM has no GUI, it is more convenient to interact with the victim VM over SSH than through its console, so you can launch the victim VM in **headless mode**.

On the *attacker VM*, run
```shell
$ sudo apt-get update
$ sudo apt-get upgrade
$ sudo apt-get dist-upgrade
# Install any tool you like: vs code, terminator, etc. (see lab sessions)
# Reboot the VM
$ git clone https://github.com/ku-leuven-msec/secure-software-and-hacking-assignment
$ cd secure-software-and-hacking-assignment
# The command below installs the server files in the student home folder on the victim VM
$ cat server.tar.gz | ssh -p 2222 student@<HOST_IP> "extract_server -" 
```

The *victim VM* has a user `student` (password: `student`) which you can use to launch the server applications for the different scenarios.
**Note that this user is not in the `sudo` group and, therefore, cannot change the system environment or run programs with elevated privileges!**
For this reason, it might be a good idea to mark the virtual disk of the victim VM as ["Immutable"](https://www.kicksecure.com/wiki/Read-only#VirtualBox) (do this after you copied the server files to the victim VM).
This option will undo every change on the file system when the VM reboots.
If an exploit fails and changes something on the system, you can easily go back to the original VM image by simply rebooting the VM.
Remember that the purpose of the victim machine is only to be attacked, and you should develop your exploits on the attacker machine, not on the victim machine.

## Launching the Server Application
On the *victim VM*, use the `launch_scenario` program to set up the scenario automatically.
For example:
```shell
$ ~/server/launch_scenario 1
$ ~/server/launch_scenario 4_asan #launch scenario 4 and use the version compiled with address sanitizer
```
This program sets the required system parameters, restores the contents of the files in `server_data`, removes the log file, and starts the server application.
The program also automatically restarts the server application whenever it terminates with an error.
**You can rely on this behavior in your exploits.**
When launched, the server changes its working directory to `/home/student/server/server_data`.
You may assume the running server instance you attack is not widely used by other actors and runs idle most of the time.
You can try the server by loading a web page in a browser (http://<HOST_IP>:8080/index.html)
Have a look at the [Useful Tools section](tools_and_info.md#useful-tools) on how to use `curl` and `nc` to communicate with the server application in your exploits.

**Interesting note:** notice how the file permissions of the `launch_scenario` program are `-rwsrwx--x`.
The execute permission for the user is `s` instead of `x` which means that a regular user can execute the program with the same permissions as the file owner, i.e., root.
This means you can launch this program as the root user without `sudo` and a successful exploit will grant root privileges to the keylogger.
Linux programs like `sudo` and `passwd` work the same way.
