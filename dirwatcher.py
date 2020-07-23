__author__ = "Albina Tileubergen-Thomas"

import signal
import time
import logging
import argparse
import os
import logging.handlers
import errno

logger = logging.getLogger(__name__)
files = {}
exit_flag = False


def find_magic_word(path, start_line, magic_text):
    """ Searches for magic text from given file and finds which line at """
    # logger.info(f"Searching {path} for instances of {magic_text}")
    line_number = 0
    with open(path) as f:
        for line_number, line in enumerate(f):
            if line_number >= start_line:
                if magic_text in line:
                    logger.info(
                        f'{magic_text} found on line {line_number + 1} in {path}'
                    )
    return line_number + 1


def watch_directory(args):
    """ Watches the directory for added and deleted files, 
    if the directory does not exist will create one.
    """
    file_list = os.listdir(args.directory)
    added_files(file_list, args.extension)
    removed_files(file_list)
    for f in files:
        files[f] = find_magic_word(
            os.path.join(args.directory, f),
            files[f],
            args.magic_text
        )


def added_files(file_list, ext):
    """ Checks the directory if the new file was added """
    global files
    for f in file_list:
        if f.endswith(ext) and f not in files:
            files[f] = 0
            logger.info(f'{f} added to the watchlist')
    return file_list


def removed_files(file_list):
    """ Checks for file if it is not in the dictionary,
    then have to remove the file """
    global files
    for f in list(files):
        if f not in file_list:
            logger.info(f'{f} removed from watchlist')
            del files[f]
    return file_list


def signal_handler(sig_num, frame):
    """ This is a signal handler for SIGTERM and SIGINT... """
    logger.warning("Recieved " + signal.Signals(sig_num).name)
    global exit_flag
    exit_flag = True


def create_parser():
    parser = argparse.ArgumentParser(
        description="Checks the directory of text files for magic string.")
    parser.add_argument('-i', '--interval', type=float,
                        default=1.0, help="Number of seconds for magic words")
    parser.add_argument('-e', '--extension', type=str,
                        default='.txt', help="Text file extension to watch for.")
    parser.add_argument('directory', help="Directory to watch")
    parser.add_argument('magic_text', help="The magic text to watch.")
    return parser


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
    logger.setLevel(logging.DEBUG)
    start_time = time.time()
    logger.info(
        '\n'
        '-----------------------------\n'
        f'   Running {__file__}\n'
        f'   PID is {os.getpid()}\n'
        f'   Started on {start_time:.2f}\n'
        '-----------------------------\n'
    )
    parser = create_parser()
    args = parser.parse_args()

    logger.info(
        f'Watching directory: {args.directory}, '
        f'File Extension: {args.extension}, '
        f'Polling Interval: {args.interval}, '
        f'Magic Text: {args.magic_text}'
    )

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while not exit_flag:
        try:
            watch_directory(args)
        except OSError as e:
            if e.errno == errno.ENOENT:
                logger.error(f'{args.directory} directory not found')
                time.sleep(2)
            else:
                logger.error(e)

        except Exception as e:
            logger.error(f'UNHANDLED exception {e}')
        time.sleep(args.interval)

    up_time = time.time() - start_time
    logger.info(
        '\n'
        '-----------------------------\n'
        f'   Stopped {__file__}\n'
        f'   Uptime was {up_time:.2f}\n'
        '-----------------------------\n'
    )
    logging.shutdown()


if __name__ == '__main__':
    main()
