import os
import git


# 添加提交用户 邮箱
def git_user(repo_git, **user_info):
    for key in user_info:
        repo_git.config("--global", "user.{}".format(key), "%s" %(user_info[key]))


class Vault:
    def __init__(self, vault_name, vault_dir_path, remote_path_template, user_info):
        self.vault_name, self.vault_dir_path, self.remote_path_template, self.user_info = \
            vault_name, vault_dir_path, remote_path_template, user_info
        self.repo, self.repo_git, self.remote = self.init(
            vault_name, vault_dir_path, remote_path_template, user_info)


    # 初始化vault
    def init(self, vault_name, vault_dir_path, remote_path_template, user_info):
        vault_path = os.path.join(vault_dir_path, vault_name)
        remote_path = remote_path_template.format(vault_name)

        local_exists = lambda: os.path.exists(vault_path)
        remote_exists = lambda repo: repo is not None and repo.__class__ is git.Repo

        if not local_exists():
            repo = git.Repo.clone_from(remote_path, to_path=vault_path, branch="main")
            if not remote_exists(repo):
                os.makedirs(vault_path)
                repo = git.Repo.init(path=vault_path, branch="main")
                remote = repo.create_remote('origin', remote_path)
            else:
                remote = repo.remote()
                
            repo_git = repo.git()
            git_user(repo_git, **user_info)

            with open(os.path.join(vault_path, 'README.md'), 'w') as f:
                f.write(f'# S-Note Vault {vault_name}\n---\nWelcome.\n')
            if remote.refs:
                remote.pull()
            repo_git.add('-A')
            repo_git.commit('-m', 'auto commit')
            remote.push()
        else:
            try:
                repo = git.Repo(vault_path)
            except git.exc.InvalidGitRepositoryError:
                dot_git = os.path.join(vault_path, '.git')
                if os.path.exists(dot_git):
                    os.rmdir(dot_git)
                repo = git.Repo.init(path=vault_path, branch="main")

            
            repo_git = repo.git()
            git_user(repo_git, **user_info)

            
            if len(repo.remotes) == 0:
                remote = repo.create_remote('origin', remote_path)
            else:
                remote = repo.remote()
            
            if remote.url != remote_path:
                remote.set_url(remote_path)
                

        return repo, repo_git, remote


    def write(self, relative_path, content, commit_msg, **kwargs):
        vault_path = os.path.join(self.vault_dir_path, self.vault_name)
        file_dir_name = os.path.join(vault_path, os.path.dirname(relative_path))
        if not os.path.exists(file_dir_name):
            os.mkdirs(file_dir_name)
        file_path = os.path.join(vault_path, relative_path)
        with open(file_path, 'w') as f:
            f.write(content)
        self.repo_git.add(relative_path)

        try:
            if self.remote.refs:
                self.remote.pull(force=True)
            self.repo_git.add('-A')
            self.repo_git.commit('-m', commit_msg)

        except git.exc.GitCommandError as e:
            print(e)
        try:
            self.remote.push()
        except git.exc.GitCommandError as e:
            print(e)
            

if __name__ == "__main__":
    vault_name = 'q1'
    vault_dir_path = r'C:\git_repos\test_vault_dir'
    remote_path_template = "http://192.168.4.200:8000/danim/{}.git"
    user_info = { 'name': 'danimeo', 'email': 'danimeon@outlook.com' }

    v = Vault(vault_name, vault_dir_path, remote_path_template, user_info)

    branches = v.remote.refs
    for item in branches:
        print(item.remote_head)

    print(v.repo.refs, v.repo.head, v.repo.head.ref)

    # v.write('logs/med_logs.txt', '001 0832,0924 tmxt24,1 s?/7\n002 0832,2132 tmxt48,2 s?/7\n', 'log: took meds `tmxt24,1` `tmxt48,2`')

    v.write('logs/med_logs.txt', '001 0832,0924 tmxt25,1 s?/7\n002 0832,2132 tmxt10,2 s?/7\n003 ???\n', 'med_logger: changed logs `001` `002`')
