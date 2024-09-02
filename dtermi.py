import json
import os
import re
import importlib
from threading import Thread
import time
from itertools import zip_longest

# os.system('python3 -m pip install rich')
from rich.console import Console
from rich.table import Table


def displayable_str(_str: str, **values):
    _str = _str.format(**values)
    _str = _str.encode('unicode_escape').replace(b'\\\\', b'\\').decode("unicode_escape")
    return _str


def clear():
    print('\033[2J', end='')


class DT:
    def __init__(self, dt_filename):
        with open(dt_filename, 'r', encoding='utf-8') as file:
            self.conf = json.load(file)
        
        self.module: importlib.ModuleType = None
        self.updating = False
        self.updating_thread: Thread = None
        
        self.console = Console()
        
    def clear_content(self):
        print('\033[{};{}H\033[K\033[1B'.format(1 + self.conf['head']['top'] + self.conf['head']['height']
                                                  + self.conf['main_view']['top'], 
                                                1 + self.conf['head']['left']),
            sep='', end='', flush=True
        )
        

    def print_head(self, head=None):
        if head is not None and isinstance(head, str):
            print(
                # Head
                '\033[{};{}H'.format(1 + self.conf["head"]["top"], 
                                     1 + self.conf["head"]["left"]),
                displayable_str(head, **self.conf),
                sep='', end='', flush=True
            )
        
    def print_prompt(self):

        print(
            # Prompt
            '\033[K\033[1B',

            '\033[{};{}H'.format(1 + self.conf["head"]["top"] + self.conf['head']['height']
                                   + self.conf['main_view']['top'] + self.conf['main_view']['height']
                                   + self.conf['prompt']['top'], 
                                 1 + self.conf['prompt']['left']),
            self.conf['prompt']['content'], 
            '\033[0K',
            '\033[s',
            sep='', end='', flush=True
        )

    def update(self, content=''):
        print('\033[s', end='')

        self.clear_content()
        
        if self.module is not None:
            
            table_1 = Table(title="[bold]:page_facing_up: 列表[/bold]", title_justify='left', title_style='bold', show_header=False, expand=True, show_edge=False)
            # [table.add_column(justify="left") for i in range(self.module.conf["list_view_n_cols"])]

            table_2 = Table(title="[bold]:zap: 记录[/bold]", title_justify='left', title_style='bold', show_header=False, expand=True, show_edge=False)
            # [table.add_column(justify="left") for i in range(self.module.conf["list_view_n_cols"])]

            lst_1 = list(zip_longest(*[iter(self.module.conf["list_view_content"])] * self.module.conf["list_view_n_rows"], fillvalue=' '))
            if lst_1:
                lst_1[-1] += (' ',) * (len(lst_1[0]) - len(lst_1[-1]))
                [table_1.add_row(*s, style="white") for s in zip(*lst_1)]

            lst_2 = list(zip_longest(*[iter(self.module.conf["log_view_content"])] * self.module.conf["log_view_n_rows"], fillvalue=' '))
            if lst_2:
                lst_2[-1] += (' ',) * (len(lst_2[0]) - len(lst_2[-1]))
                [table_2.add_row(*s, style="white") for s in zip(*lst_2)]
            print(
                '\033[{};{}H'.format(1 + self.conf["head"]["top"] + self.conf['head']['height']
                                      + self.conf['main_view']['top'],
                                 1 + self.conf['main_view']['left']),
                sep='', end='', flush=True)
            

            self.console.print(content, end='')

            self.console.print(table_1)
            print('\n', sep="", end="", flush=True)
            self.console.print(table_2)
            

            print(
                '\033[{};{}H'.format(1 + self.conf["head"]["top"] + self.conf['head']['height']
                                      + self.conf['main_view']['top'] + self.conf['main_view']['height'],
                                      + self.conf['prompt']['top'],
                                 1 + self.conf['main_view']['left']),
                '\033[u',
                sep='', end='', flush=True)


    def load_mod(self, mod_filename=''):
        if not mod_filename:
            mod_filename = self.conf['mod']['path']
        mod_filename = os.path.basename(mod_filename).replace('.py', '')
        self.module = importlib.import_module('mod.' + mod_filename)


    def mod_loop(self, **args):
        while self.updating:
            self.module.__callback__(**args)

            self.update(content=self.module.conf["content"])

            time.sleep(self.conf["updating_interval_seconds"])


    def mainloop(self):
        clear()
        self.print_head(self.conf["welcome"])
        self.print_prompt()

        self.updating_thread = Thread(target=self.mod_loop)
        self.updating = True
        self.updating_thread.start()

        while True:
            cmd = input()

            if cmd in (':q', ':Q', 'exit', 'quit'):
                clear()
                print('\033[1;1H')
                self.updating = False
                exit()
            else:
                self.module.__handle__(cmd)

            self.update(content=self.module.conf["content"])
            self.print_prompt()


def create_DT(dt_filename, mod_filename=''):
    dt = DT(dt_filename)
    dt.load_mod(mod_filename)
    dt.mainloop()


if __name__ == '__main__':
    create_DT('conf/synctron.dt.json', mod_filename='med_logger')

