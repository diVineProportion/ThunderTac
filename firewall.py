import subprocess, ctypes, os, sys
from subprocess import Popen, DEVNULL

def check_admin():
    """ Force to start application with admin rights """
    try:
        isAdmin = ctypes.windll.shell32.IsUserAnAdmin()
    except AttributeError:
        isAdmin = False
    if not isAdmin:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)


def add_rule(rule_name, program, direction='outbound', action='allow', enabled=False)                                                                                                                                                                                                                                                                                                             file_path):
    """ Add rule to Windows Firewall """
        subprocess.run(
        [
            'netsh', 'advfirewall', 'firewall',
            'add', 'rule', f'name={rule_name}',
            f'direction={direction}', f'action={action}', 
            f'enable={"yes" if enabled else "no"}', f'program={program}',
        ],
        check=True,
        stdout=DEVNULL,
        stderr=DEVNULL
    )


def modify_rule(rule_name, enabled=True):
    """Enable or Disable a specific rule"""
    subprocess.run(
        [
            'netsh', 'advfirewall', 'firewall',
            'set', 'rule', f'name={rule_name}',
            'new', f'enable={"yes" if enabled else "no"}',
        ],
        check=True,
        stdout=DEVNULL,
        stderr=DEVNULL
    )

if __name__ == '__main__':
    
    target_name = "ThunderTac"
    target_path = "K:\\_PROGRAMMING\\.py\\PycharmThunderTac\\testing\\main.exe"

    check_admin()
    add_rule(target_name, target_path)
    modify_rule(target_name, 1)