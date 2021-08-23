import argparse




def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--times', type=int, default='3')
    parser.add_argument('-s', '--stride', type=int, default='10')
    
    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    print(args.times)
    print(args.stride)



