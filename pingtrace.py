import platform
import subprocess
import ipaddress
import re


def validate_domain(domain):
    pattern = re.compile(
        r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
        r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
        r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
        r'([a-zA-Z]{2,13}|dn42|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
    )
    if pattern.match(domain):
        return True
    return False


def validate_ip(ip_string):
    try:
        if ip_string.isdigit() and 10 >= len(ip_string) > 7:
            ip_string = int(ip_string)
        ip_object = ipaddress.ip_address(ip_string)
        return str(ip_object)
    except ValueError:
        # print("The IP address " + ip_string + " is not valid")
        return False


def ping(ip, version=0):
    os = platform.system().lower()
    if os == 'darwin':
        commands = ['ping', '-c', '4', '-t', '10', ip]
    else:
        commands = ['ping', '-c', '4', '-w', '10', ip]
    if version == 4:
        commands.insert(1, '-4')
    try:
        out_bytes = subprocess.check_output(commands, timeout=15)
        out_text = out_bytes.decode('utf-8')
        return out_text
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        code = e.returncode
        return out_bytes.decode('utf-8')
    except subprocess.TimeoutExpired as e:
        return "ping " + ip + " timed out after 15 seconds"


def mtr(target, version=0):
    commands = ['mtr', '--report', '--report-wide', '-c', '5', '-Z', '10', target]
    if version == 4:
        commands.insert(1, '-4')
    try:
        out_bytes = subprocess.check_output(commands,
                                            timeout=15)
        out_text = out_bytes.decode('utf-8')
        return out_text
    except subprocess.TimeoutExpired as e:
        return "mtr " + target + " timed out after 15 seconds"
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        code = e.returncode
        return "mtr " + target + " failed"
#        return out_bytes.decode('utf-8')


def traceroute(target, version=0):
    commands = ['traceroute', '-w2', target]
    if version == 4:
        commands.insert(1, '-4')
    try:
        out_bytes = subprocess.check_output(commands, timeout=25)
        out_text = out_bytes.decode('utf-8')
        return out_text
    except subprocess.TimeoutExpired as e:
        out_bytes = e.output
        out_text = out_bytes.decode('utf-8')
        return out_text
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        code = e.returncode
        return "traceroute " + target + " failed"


def do_action(action, target):
    if action == "ping":
        return ping(target)
    elif action == "mtr":
        return mtr(target)
    elif action == "trace":
        return traceroute(target)
    if action == "ping4":
        return ping(target, 4)
    elif action == "mtr4":
        return mtr(target, 4)
    elif action == "trace4":
        return traceroute(target, 4)
    else:
        return "Unknown Action Error" + action


def lg(action, target):
    vi = validate_ip(target)
    if vi:
        return do_action(action, vi)
    elif validate_domain(target):
        return do_action(action, target)
    else:
        return "Invalid " + target + " Target"
