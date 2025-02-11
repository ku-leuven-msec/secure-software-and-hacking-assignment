void build_200_response_read(struct file_info* file_info, char* response_buf, size_t* response_len) {

    struct stat buf;

    int fd = open(file_info->file_name, O_RDONLY);
    if (fd != -1) {
        char* extension = strrchr(file_info->file_name, '.');
        if (extension == NULL) extension = ".";
        const char* mime_type = ext_to_mime(extension + 1);
        strcpy(file_info->mime_type, mime_type);
        
        fstat (fd, &buf);
        file_info->file_size = buf.st_size;
        
        size_t remaining_lenght = 0x800; //2KiB
        snprintf(response_buf, remaining_lenght, "HTTP/1.1 200 OK\r\nContent-Type: %s\r\nContent-Length: %lu\r\n\r\n", mime_type, file_info->file_size);
        *response_len = strlen(response_buf);

        remaining_lenght -= *response_len;
        ssizet_t read_len = read(fd, response_buf + *response_len, remaining_lenght);
        if (read_len == -1) {
            //L2
            build_500_response(response_buf, response_len);
        } else {
            *response_len += read_len;
        }
        //L3
        close(fd);
        printf("File %s is read\n", file_info->file_name);

    } else {
        //L1
        build_404_response(response_buf, response_len);
    }
    //L4
    return;
}

