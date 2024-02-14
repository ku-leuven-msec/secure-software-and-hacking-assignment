#include <stddef.h>
#include <sys/socket.h>
#include <linux/limits.h>

struct credentials {
  char* user_name; //null-terminated string, struct ownes this buffer
  char passwd_sha256[32]; //not null-terminated
};

struct file_info {
  char file_name[PATH_MAX];
  bool (*validate_file_name_fn)(const char*);
  volatile long file_size;
};

//Logs arg:message to stdout and to a file
//Returns 0 on success
int log_message(const char* message, ssize_t message_len, int* client_fd);

//Returns true if arg:header is authenticated
bool authenticate(const char* header);

//Builds a 200 response in arg:response_buf, and appends arg:body to the file
void build_200_response_append(const char* file_name, const char* body,
  int body_len, char* response_buf, size_t* response_buf_len);

//Parses the request in arg:request_buf, logs only (!!) the request header,
//receives any remaining body data, executes the request, and builds a
//response in arg:response_buf
//Arg:file_info is already allocated
void parse_request(int client_fd, struct file_info* file_info,
  char* request_buf, ssize_t* request_buf_len, char* response_buf,
  size_t* response_buf_len);

//Receives the whole request, calls `parse_request`, and sends the response back
//to the client using its file descriptor
void handle_client(int client_fd);


// ===== Functions without (intentional) bugs ================================//

//Launches the `stats` program and fills the arg:stats_buffer with its stdout
void get_server_stats(char* stats_buffer, size_t stats_buf_len);

//Maps the file extension to a HTTP content-type string
//The returned string is a global constant
const char* ext_to_mime(const char* file_ext);

//Extracts the file name from arg:header
//Returns null on error, else: passes ownership of the returned file name to
//the caller
char* extract_file_name(const char* header);

//Extracts and returns the HTTP Content-Length field as an int
int extract_content_length(const char* header);

//Extracts the HTTP Authorization field, decodes the base64 value, and hashes
//the passwd with SHA256
//Returns the credentials
bool extract_credentials(const char* header, struct credentials* credentials);

//Returns true if arg:file_name is inside the `server_data` directory
bool validate_file_name(const char* file_name);

//Builds a 200 response with the contents of the file in arg:response_buf
void build_200_response_read(struct file_info* file_info, char* response_buf,
  size_t* response_buf_len);

//Builds a 200 response in arg:response_buf, and creates (or overwrites) the
//file with arg:body
void build_200_response_create(const char* file_name, const char* body,
  int body_len, char* response_buf, size_t* response_buf_len);

//Build and error response in arg:response_buf
void build_400_response(char* response_buf, size_t* response_buf_len);
void build_401_response(char* response_buf, size_t* response_buf_len);
void build_403_response(char* response_buf, size_t* response_buf_len);
void build_404_response(char* response_buf, size_t* response_buf_len);
void build_411_response(char* response_buf, size_t* response_buf_len);
void build_413_response(char* response_buf, size_t* response_buf_len);
void build_418_response(char* response_buf, size_t* response_buf_len);
void build_500_response(char* response_buf, size_t* response_buf_len);

//The entry function for each new connection thread
//Directly calls `handle_client`
void* handle(void* arg);

//Nothing to see here
void totally_unsuspicious_code();

//Prints the process ID to stdout
void print_pid();

//Minor initializations
void init();

//Creates and binds a socket, spawns a new thread for each incomming connection
int main(int argc, char* argv[]);
