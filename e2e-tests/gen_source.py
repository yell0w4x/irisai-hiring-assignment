import sys
import random


def profiles():
    MAX_WALL_HEIGHT = 30
    WALLS_COUNT = 10
    MAX_SECTIONS_COUNT = 200
    return [[random.randint(0, MAX_WALL_HEIGHT) for _ in range(random.randint(1, MAX_SECTIONS_COUNT))] for _ in range(WALLS_COUNT)]


def main(args=sys.argv):
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} FILE')
        return 1

    fn = sys.argv[1]
    with open(fn, 'w') as f:
        f.write('\n'.join(' '.join([str(item) for item in p]) for p in profiles()))


if __name__ == '__main__':
    main()
