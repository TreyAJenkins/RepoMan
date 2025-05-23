# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from pathlib import Path
from gitRepo import gitRepo
from gitRepo.github import GitHub
from gitRepo.bundler import Bundler
import argparse
from rich.traceback import install
import json
install(show_locals=True)

parser = argparse.ArgumentParser()
parser.add_argument("--bundle", help="Bundle storage", action="store_true")
parser.add_argument("--file", help="Mirror from file", type=Path, required=False)
parser.add_argument("--user", help="Mirror all users repos", type=str, required=False)
parser.add_argument('--storage', help="Storage location", type=Path, default=Path("./storage"))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    args = parser.parse_args()
    repoman = gitRepo.GitRepo(args.storage)
    github = GitHub(repoman)

    if args.user:
        github.mirror_user_repos(args.user)
    if args.file:
        dat = args.file.open().read()
        for line in dat.splitlines():
            github.mirror_repo(line.strip().replace("'", '').replace('"', ''))
    if args.bundle:
        bundler = Bundler(args.storage)
        bundler.add_all_repos()
        with open(args.storage / 'metadata.json', 'w') as f:
            json.dump(bundler.datastore, f)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
