import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("n", help="total numbers")
parser.add_argument("p", help="file prefix")
parser.add_argument("s", help="file suffix")
parser.add_argument("f", help="file location")
args = parser.parse_args()
config = vars(args)

path = os.path.join(os.getcwd(), config["f"])
for filename in os.listdir(path):
    prefix = config["p"]
    num = os.path.splitext(filename)[0].removeprefix(prefix)
    num = num.zfill(int(config["n"]))
    new_filename = prefix + num + "." + config["s"]
    print(os.path.join(path, filename), os.path.join(path, new_filename))
    os.rename(os.path.join(path, filename), os.path.join(path, new_filename))
