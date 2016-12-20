import os
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db_user', type=str, nargs=1)
    parser.add_argument('--db_name', type=str, nargs=1)
    parser.add_argument('--db_password', type=str, nargs='*')

    args = parser.parse_args()
    return {
        '__DB_NAME__': args.db_name[0],
        '__DB_USER__': args.db_user[0],
        '__DB_PASSWORD__': args.db_password[0] if args.db_password else ''
    }


def replace_file_args(args, in_file, out_file):
    with open(in_file, 'r') as fin:
        with open(out_file, 'w') as fout:
            out_lines = []
            for line in fin.readlines():
                for key, value in args.items():
                    line = line.replace(key, value)
                out_lines.append(line)
            fout.write(''.join(out_lines))


if __name__ == '__main__':
    args = parse_args()

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_conf_files = [
        (
            os.path.join(BASE_DIR, 'default.cnf'),
            os.path.join(BASE_DIR, 'rupture.cnf')
        ),
        (
            os.path.join(BASE_DIR, 'default.sql'),
            os.path.join(BASE_DIR, 'rupture.sql')
        )
    ]

    for conf in db_conf_files:
        replace_file_args(args, conf[0], conf[1])
