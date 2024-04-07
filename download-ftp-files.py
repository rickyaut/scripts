import logging
from logging.handlers import TimedRotatingFileHandler

from ftplib import FTP
from datetime import datetime, timedelta
import os
import sys

if len(sys.argv) != 8:
    print(
        """
          Usage: python3 download-ftp-files.py <HOST> <USERNAME> <PASSWORD> <SRC_FOLDER> <DEST_FOLDER> <MAX_DAYS> <STORAGE_CAPACITY>
          Install dependency packages by running: python3 -m pip install -r requirements.txt
          Samples: python3 ~/scripts/download-ftp-files.py '10.0.0.55' 'root' '12345678' '/mnt/record' 'videos' 2 2.5
            or curl -sSL https://raw.githubusercontent.com/rickyaut/scripts/main/download-ftp-files.py | python3 - '10.0.0.55' 'root' '12345678' '/mnt/record' 'videos' 2 2.5
            or wget -O - https://raw.githubusercontent.com/rickyaut/scripts/main/download-ftp-files.py | python3 - '10.0.0.55' 'root' '12345678' '/mnt/record' 'videos' 2 2.5
          """
    )
    sys.exit(1)

HOST = sys.argv[1] # '10.0.0.55'
USERNAME = sys.argv[2] # 'root'
PASSWORD = sys.argv[3] # '12345678'
SRC_FOLDER = sys.argv[4] # "/mnt/record"
DEST_FOLDER = sys.argv[5] # "videos"
MAX_DAYS = int(sys.argv[6]) # 2
STORAGE_CAPACITY_IN_GB = float(sys.argv[7]) # 2.5*1024*1024*1024
STORAGE_CAPACITY_IN_BYTES = STORAGE_CAPACITY_IN_GB* 1024*1024*1024
NOW = datetime.now()

def init_log():
    # Create a log directory if it doesn't exist
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    # Create a custom formatter for the log messages
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create a timed rotating file handler that rotates logs daily
    log_filename = os.path.join(log_dir, NOW.strftime('%Y-%m-%d') + '.log')
    file_handler = TimedRotatingFileHandler(log_filename, when='midnight', interval=1, backupCount=7)
    file_handler.setFormatter(log_formatter)

    # Set up the root logger with the custom file handler
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.INFO)

def list_ftp_files_recursive(ftp, folder):
    def _list_files_recursive(ftp, folder):
        files = []
        files_details = []

        # List files and directories in the current directory
        ftp.retrlines('LIST ' + folder, files.append)
        for line in files:
            parts = line.split(maxsplit=8)
            if parts[0] == 'total':
                continue
            filename = parts[-1]
            mtime_str = ' '.join(parts[5:8])
            if len(parts[7].split(':')) == 2:
                mtime = datetime.strptime(mtime_str, '%b %d %H:%M')
                mtime = mtime.replace(year = NOW.year)
                mtime = mtime if mtime < NOW else mtime.replace(year = NOW.year - 1)
            else:
                mtime = datetime.strptime(mtime_str, '%b %d %Y')
            if filename in ('.', '..'):
                continue
            elif parts[0].startswith('d') and mtime > NOW - timedelta(days=MAX_DAYS):
                # If it's a directory, list its files recursively
                files_details.extend(_list_files_recursive(ftp, folder + '/' + filename))
            elif mtime > NOW - timedelta(days=MAX_DAYS):
                # If it's a file, append its details to the list
                file_path = folder + '/' + filename

                files_details.append(file_path)

        return files_details

    # List files recursively
    files = _list_files_recursive(ftp, folder)

    # Sort files by modification time (newest first)
    files.sort(key=lambda x: x[1], reverse=True)

    return files

def download_ftp_file(ftp, remote_file_path, local_file_path):
    with open(local_file_path, 'wb') as local_file:
        logging.info(f'downloading {remote_file_path} into {local_file_path}')
        ftp.retrbinary('RETR ' + remote_file_path, local_file.write)

def get_folder_size(folder_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            total_size += os.path.getsize(file_path)
    return total_size

def list_files_recursive(folder):
    for root, dirs, files in os.walk(folder):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if(not os.listdir(dir_path)):
                logging.info(f'removing empty folder {dir_path}')
                os.rmdir(dir_path)

        for file in files:
            file_path = os.path.join(root, file)
            yield file_path

def delete_old_files():
    while get_folder_size(DEST_FOLDER) > STORAGE_CAPACITY_IN_BYTES:
        file_to_be_removed = sorted(list(list_files_recursive(DEST_FOLDER)))[0]
        logging.info(f'removing {file_to_be_removed}')
        os.remove(file_to_be_removed)

def main():
    try:
        init_log()
        # Get file details from the FTP server
        with FTP(HOST) as ftp:
            # Login to the FTP server
            ftp.login(USERNAME, PASSWORD)
            files = list_ftp_files_recursive(ftp, SRC_FOLDER)
            for remote_file_path in files:
                local_file_path = remote_file_path.replace(SRC_FOLDER, DEST_FOLDER)
                if not os.path.exists(local_file_path):
                    os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
                    download_ftp_file(ftp, remote_file_path, local_file_path)
            delete_old_files()
            logging.info("finished download videos")
    except Exception as e:
        logging.error(f'An error occurred: {e}')

if __name__=='__main__':
    main()
