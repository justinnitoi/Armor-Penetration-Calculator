def create_logger(file_name):
    def log(msg):
        print("{}: {}".format(file_name, msg))

    return log
