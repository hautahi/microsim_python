from CommandParser import CommandParser


def main():
    command_parser = CommandParser()
    settings = command_parser.execute('commands.txt')
    households = command_parser.generate_households()

    for hh in households:
        for person in hh.people:
            pass


if __name__ == '__main__':
    main()
