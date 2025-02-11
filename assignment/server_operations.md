
## The Server Application
**Read this section thoroughly!** 
You need to know how the server operates before you can exploit it.

The vulnerable HTTP server application is written in C, runs with root privileges on a Linux host, and accepts connections on port 8080.
We compiled the server application into x86_64 ELF binaries without debug symbols for all scenarios.
We used clang 16.0.6 as the compiler and compiled with optimization flags that include `-O1 -fno-omit-frame-pointer -fno-inline-functions -fno-optimize-sibling-calls`.
The remote victim machine runs a firewall that blocks all incomming and outgoing connections on any port, except for port 8080 (the server port) and port 22 (ssh).

### Server Operations
The server accepts HTTP GET, POST, and PUT requests that interact with files in the `server_data` directory:
* GET sends the requested file to the client.
* POST appends the HTTP body to the specified file.
It returns 404 if the specified file does not exist.
* PUT creates the specified file and fills it with the HTTP body.
The server overwrites the file if it already exists.
All file operations are restricted to the `server_data` directory.

The PUT request requires authentication using [HTTP Basic Authentication](https://en.wikipedia.org/wiki/Basic_access_authentication).
It decodes the provided base64 credentials, hashes the password (SHA256, without salt), and checks if the credentials are correct.
There is only one authenticated user and password pair and there is no connection to intercept between the server and an actor that knows the password.
You should also (obviously) not try to reverse the hashed password.
In other words, do not waste time trying to get the plaintext password.

The server application spawns a **new thread with a thread-local stack for each incoming connection**.
When receiving a request, the server first reads the whole header (**ending with "\r\n\r\n"**), parses it, extracts the "Content-Length" field, and then reads N bytes of the body, with N the given content length.
The server logs the header of each request it receives in a log file `server.log`.
If your request does not contain the header ending ("\r\n\r\n") or has a "Content-Length" field larger than its body, the server will wait for the client to send more data (or until the client closes the connection).
**Be sure to experiment with this blocking behavior!**
The "Content-Length" field is optional for GET requests.

