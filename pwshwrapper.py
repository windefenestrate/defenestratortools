import subprocess

class PowerShellGetError(Exception): pass

def run(cmd: str) -> subprocess.CompletedProcess:
    """Run a command within Windows PowerShell.

    Args:
        cmd (str): the command to run.

    Returns:
        subprocess.CompletedProcess: the resulting process. Use `returncode` to determine whether to raise an exception (it is recommended to pipe in the decoded output of `stderr`) or continue executing.
    """
    completed = subprocess.run(['powershell', '-Command', cmd], capture_output=True)
    return completed

def get(val: str):
    """Get a PowerShell value. Internally, this is done by calling `'Write-Host {val}'` in Windows PowerShell and converting the output into a native Python value.

    Args:
        val (str): the value to get.

    Raises:
        PowerShellGetError: if an error happens during retrieving a value, this exception will be raised.

    Returns:
        a native Python value corresponding to the retrieved output.
    """
    completed = subprocess.run(['powershell', '-Command', f'Write-Host {val}'], capture_output=True)
    stdout = completed.stdout.decode('utf-8')
    stderr = completed.stderr.decode('utf-8')
    if completed.returncode != 0:
        raise PowerShellGetError(stderr)
    return convert_from_string(stdout)

def convert_from_string(data: str):
    """Convert a string from a PowerShell output stream to an appropriate Python value.

    Args:
        data (str): the string to convert.
    """
    if data == 'True':
        return True
    elif data == 'False':
        return False
    elif data.isdigit():
        return int(data)
    elif data.isnumeric():
        return float(data)
    else:
        return data

if __name__ == '__main__':
    info = run('Write-Host "Hello, world!"')
    print(info.returncode)
    print(info.stdout)
    print(info.stderr)