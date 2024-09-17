import json
import re
import datetime
from fractions import Fraction

import os
import pypinyin
from vault_mgr import Vault


conf = {
  "name": "med-logger",
  "version": "2024.08a",
  "content": "",
  "list_view_content": [],
  "log_view_content": [],
  "commands": {
      "add": {
          "pattern": r"^add (.+) (.+) (.+) (.+)$",
          "format": "add {0} {1} {2} {3}"
      },
  },
  "list_view_n_rows": 6,
  "log_view_n_rows": 7,
}


data = {
    "vault_conf": {
        "vault_name": 'snote-001',
        "vault_dir_path": './test_vault_dir',
        "remote_path_template": 'http://r.danim.space/danim/{}.git',  # https://gitee.com/danimeo/snote-001.git
        "user_info": {'name': 'danim', 'email': 'danimeon@outlook.com'}
    },
    "i18n": [
        ["专注达", "Concerta"],
        ["择思达", "Strattera"],
        ["利妥思", ""],
        ["托莫西汀", "atomoxetine"],
        ["盐酸", "hydrochloride"],
        ["胶囊", "capsules"],
        ["哌甲酯", "methylphenidate"],
        ["片", "tablets"], 
        ["缓释", "extended-release"],
    ],
    "meds": [
        {
            "id": 1,
            "name": ["tmxt", "tm"],
            "generic_name": ["托莫西汀", "盐酸", "胶囊", ""],
            "specs": [[["利妥思", ""], 25, 7, 4], [["天方", ""], 10, 7, 2], [["正丁", ""], 10, 10, 1], [["择思达", ""], 25, 7, 1], ]
        },{
            "id": 2,
            "name": ["pjz", "pj", "zzd"],
            "generic_name": ["哌甲酯", "盐酸", "片", "缓释"],
            "specs": [[["专注达", ""], 18, 15, 1], ]
        },{
            "id": 3,
            "name": ["qzt", "qz"],
            "generic_name": ["曲唑酮", "盐酸", "片", ""],
            "specs": [[["安适", ""], 50, 12, 1], [["安适", ""], 50, 10, 2], [["美时玉", ""], 50, 10, 2], ]
        },{
            "id": 4,
            "name": ["mdp", "md"],
            "generic_name": ["米氮平", "", "片", ""],
            "specs": [[["瑞美隆", ""], 30, 10, 1], ]
        },{
            "id": 5,
            "name": ["adp", "ad"],
            "generic_name": ["奥氮平", "", "片", ""],
            "specs": [[["奥兰之", ""], 5, 10, 2], [["喜奥平", ""], 5, 7, 4], ]
        },{
            "id": 6,
            "name": ["sql", "sq"],
            "generic_name": ["舍曲林", "盐酸", "片", ""],
            "specs": [[["唯他停", ""], 50, 14, 2], [["乐元", ""], 50, 14, 2], ]
        },{
            "id": 7,
            "name": ["yzpkl", "yz"],
            "generic_name": ["右佐匹克隆", "", "片", ""],
            "specs": [[["齐梦欣", ""], 3, 14, 1], [["伊坦宁", ""], 3, 7, 1], [["迪沙", ""], 1, 12, 3], ]
        },{
            "id": 8,
            "name": ["aszl", "as"],
            "generic_name": ["艾司唑仑", "", "片", ""],
            "specs": [[["", "常州四药"], 1, 0, 1], [["华意", "华中药业"], 1, 10, 1]]
        },{
            "id": 9,
            "name": ["asxtpl", "asxt"],
            "generic_name": ["艾司西酞普兰", "草酸", "片", ""],
            "specs": [[["启程", "湖南洞庭"], 10, 7, 1], [["百适可", ""], 10, 0, 0], ]
        },{
            "id": 10,
            "name": ["zbt", "zb"],
            "generic_name": ["唑吡坦", "酒石酸", "片", ""],
            "specs": [[["思诺思", ""], 10, 7, 1], ]
        },{
            "id": 11,
            "name": ["alpz", "al"],
            "generic_name": ["阿立哌唑", "", "片", "口崩"],
            "specs": [[["博思清", ""], 5, 10, 2], ]
        },{
            "id": 12,
            "name": ["fnxa", "fn"],
            "generic_name": ["非那雄胺", "", "片", ""],
            "specs": [[["天保发", ""], 1, 10, 3], ]
        },{
            "id": 13,
            "name": ["apzl", "ap"],
            "generic_name": ["阿普唑仑", "", "片", ""],
            "specs": [[["广西区医院-1", ""], 0.4, 14, 1], [["广西区医院-2", ""], 0.4, 14, 1], ]
        },{
            "id": 14,
            "name": ["bwsn", "b"],
            "generic_name": ["丙戊酸钠", "", "片", ""],
            "specs": [[["广西区医院-1", ""], 200, 30, 1], ]
        }
    ],
    "status": {
        3: ["done", (5, 2), (1, 2)],
    },
    "logs": {
        "filename": "meds_2024n.txt",
        "dir_relative_path": "logs/medicine/",

        "content": [
        ]
  }
}

v = Vault(**data["vault_conf"])


title = '[bold white on blue] :pill: 服药记录器 [/bold white on blue] [cyan]v[i]{}[/i][/cyan]'.format(conf['version'])
rules = '[white]命令说明：  \\[add ]<药名><单位剂量> <服用数量> <板剩余量> <片剩余量>  # 添加记录  |  :q  # 退出[/white]'


def update(data: dict, conf: dict, rules: str, err_info='', med_list_mode='compact'):

    if med_list_mode == "compact":
        it = list("{} -> {}({})".format(
                    "; ".join(med["name"]), 
                    med["generic_name"][0], 
                    '; '.join(set(str(spec[1]) + 'mg' for spec in med["specs"])),
                    # "; ".join([("{}: {}mg" + "×{}" * (len(spec) - 2)).format(*[item if item != Fraction(0) else '?' for item in spec]) for spec in med["specs"]])
                )
            for med in data["meds"])
    else:
        it = list("{} -> {} | {}".format(
                    "; ".join(med["name"]), 
                    med["generic_name"][0], 
                    "; ".join([("{}: {}mg" + "×{}" * (len(spec) - 2)).format(*[item if item != Fraction(0) else '?' for item in spec]) for spec in med["specs"]])
                )
            for med in data["meds"])
        
    conf["list_view_content"] = it
    
    conf["log_view_content"] = list('{:0>3d} {}'.format(1 + i, log) for i, log in enumerate(data["logs"]["content"]))

    conf["content"] = '{}\n\n{}\n\n{}'.format(title, rules, err_info + '\n\n' if err_info else '')

    

def get_content(user):
    """Extract text from user dict."""
    country = user["location"]["country"]
    name = f"{user['name']['first']} {user['name']['last']}"
    return f"[b]{name}[/b]\n[yellow]{country}"




def __callback__(**args):
    update(data, conf, rules)


def __handle__(command: str):

    m_ = re.match(r'(add +)?([A-Za-z_]+[^\r\n]*)', command.strip())

    if m_ is None:
        update(data, conf, rules, err_info="❌ 命令输入有误: " + command)
        return
    
    meds_taken = []

    for i, m_1 in enumerate(re.finditer(r'([A-Za-z_]+)([0-9\./]+)?[ \,]*([0-9\./]+)?', m_.group(2))):
    
        if m_1:
            # name
            name = m_1.group(1)
            if name is not None and name != '':
                name = name.strip()
            else:
                return

            # pills_taken
            pills_taken = m_1.group(3)
            if pills_taken is not None and pills_taken !='' and Fraction(pills_taken.strip()) > 0:
                if '/' in pills_taken:
                    pills_taken = Fraction(pills_taken.strip()) if len(str(Fraction(pills_taken.strip()))) < 4 else float(pills_taken.strip())
                else:
                    pills_taken = float(pills_taken.strip())
            else:
                pills_taken = Fraction(1)

            # med
            med = None
            for m in data["meds"]:
                if m is not None and name in m["name"]:
                    med = m
                    break
            else:
                if med is None:
                    med = {
                        "id": max(data["meds"], key=lambda x: x["id"])["id"] + 1,
                        "name": [name],
                        "generic_name": [f"<Unknown>", "", "", ""],
                        "specs": [("<?>", Fraction(0), Fraction(0), Fraction(0))]
                    }
                else:
                    med["name"].append(name)

            # dosage_mg_taken
            dosage_mg_taken_ = m_1.group(2)
            if dosage_mg_taken_ is not None:
                dosage_mg_taken_ = dosage_mg_taken_.strip()
                e = eval(dosage_mg_taken_)
                if re.search(r'[\+\-\*]', dosage_mg_taken_) is None:
                    a, b = Fraction(dosage_mg_taken_), float(dosage_mg_taken_)
                else:
                    a = Fraction(e)
                    if re.search(r'/', dosage_mg_taken_) is None:
                        b = float(dosage_mg_taken_)
                    else:
                        b = float(e)

                if b == e and a != e:
                    dosage_mg_taken = int(b) if str(b).endswith('.0') else b
                elif b != e and a == e:
                    dosage_mg_taken = a
                else:
                    slen = lambda x: len(str(x))
                    dosage_mg_taken, _ = sorted([a, b], key=slen)

                    if slen(a) == slen(b):
                        dosage_mg_taken = b
            else:
                dosage_mg_taken = med["specs"][0][1]


            if dosage_mg_taken not in (spec[1] for spec in med["specs"]):
                med["specs"].append(("<?>", dosage_mg_taken, Fraction(0), Fraction(0)))
            

            # pills_per_strip
            for spec in med["specs"]:
                if spec[1] == dosage_mg_taken:
                    if spec[2] > 0:
                        pills_per_strip = str(spec[2])
                    else:
                        pills_per_strip = '?'
                    break


            med_name = ''.join(pypinyin.lazy_pinyin(med["generic_name"][0], style=pypinyin.Style.FIRST_LETTER)).lower()
            timing_str = datetime.datetime.now().strftime('%m%d,%H%M')
            
            # data["logs"].append()
            data["logs"]["content"].append(f"{timing_str} {med_name}{dosage_mg_taken},{pills_taken} s{'?'}/{pills_per_strip} t{'?'}/{'?'}")
            update(data, conf, rules)
            
            log_file_path = os.path.join(data["logs"]["dir_relative_path"], data["logs"]["filename"])

            meds_taken.append((f'{med_name}{dosage_mg_taken}',f'{pills_taken}'))

    
    v.write(log_file_path, '\n'.join(data["logs"]["content"]), f'took meds: {" ".join(f"`{med_taken}`×{dsg}" for med_taken, dsg in meds_taken)}')
