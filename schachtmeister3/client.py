from argparse import ArgumentParser


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('-h', '--host', default='127.0.0.1', help='Host on which a Schachtmeister daemon is running')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT, help='Port number')
    parser.add_argument('address', help='Address(es) to be judged')
    args = parser.parse_args()




if __name__ == '__main__':
    main()
