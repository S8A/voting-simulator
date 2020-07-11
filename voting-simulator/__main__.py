# coding=utf-8
"""Simple voting system simulator for single- and multi-district elections."""


import argparse
import random as rd


def main(args):
    if args['seed']:
        rd.seed(args['seed'])
    print('..:: VOTING SYSTEM SIMULATOR ::..')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Simple voting system simulator')
    parser.add_argument('--seed')
    args = vars(parser.parse_args())
    main(args)
