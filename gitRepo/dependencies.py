from git import Repo
from urlpath import URL
from configparser import ConfigParser

class DepScanner:
    repo: Repo
    submodules = []
    filter = None

    def parseGitModules(self, contents: str):
        config = ConfigParser(allow_no_value=True)
        config.read_string(contents)
        for section in config.sections():
            if config.has_option(section, 'url'):
                submodule_path = config.get(section, 'path')
                submodule_url = config.get(section, 'url', fallback=None)
                if submodule_url is None:
                    continue
                if "../" in submodule_url:
                    submodule_url = str((self.url / submodule_url).resolve())
                if self.filter is not None and self.filter not in submodule_url:
                    continue
                if submodule_url not in self.submodules:
                    self.submodules.append(submodule_url)
        return self.submodules

    def scan(self):
        for head in self.repo.heads:
            if ".gitmodules" in head.commit.tree:
                blob = head.commit.tree['.gitmodules']
                self.parseGitModules(blob.data_stream.read().decode())
        return self.submodules


    def __init__(self, repo: Repo, filter: str = None):
        self.repo = repo
        self.url = URL(repo.remote().url)
        self.submodules = []
        self.filter = filter

        self.scan()



