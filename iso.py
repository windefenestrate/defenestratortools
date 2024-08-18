import pwshwrapper as pwsh
from distutils.dir_util import copy_tree

class ISOMountError(Exception): pass
class ISODismountError(Exception): pass
class ISOCopyError(Exception): pass

class ISOInfoWrapper:
    def __init__(self, ISO_info):
        self.attached: bool           = ISO_info['Attached']
        self.block_size: int          = ISO_info['BlockSize']
        self.device_path: str         = ISO_info['DevicePath']
        self.file_size: int           = ISO_info['FileSize']
        self.image_path: str          = ISO_info['ImagePath']
        self.logical_sector_size: int = ISO_info['LogicalSectorSize']
        self.number: int              = ISO_info['Number']
        self.size: int                = ISO_info['Size']
        self.storage_type: int        = ISO_info['StorageType']
        self.PS_computer_name: str    = ISO_info['PSComputerName']

        self.is_mounted: bool = bool(self.device_path)
        if self.is_mounted:
            self.drive_letter: str|None = pwsh.get(f'(Get-DiskImage -DevicePath "{self.device_path}" | Get-Volume).DriveLetter').strip()
        else:
            self.drive_letter = None

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f'ISO ("{self.image_path}") @ "{self.device_path}"'
    
    def mount(self):
        """Mount the associated ISO to a virtual drive.

        Returns:
            ISOInfoWrapper: a new info wrapper instance reflecting the mounted virtual drive.
        """
        return ISOInfoWrapper(mount(self.image_path))

    def dismount(self):
        """Dismount the associated ISO from a virtual drive.

        Returns:
            ISOInfoWrapper: a new info wrapper instance reflecting the dismounted virtual drive.
        """
        return ISOInfoWrapper(dismount(self.image_path))
    
    def copy(self, destination: str):
        if self.is_mounted and self.drive_letter:
            copy_tree(f'{self.drive_letter}:\\', destination)
            return self
        else:
            raise ISOCopyError('ISO not mounted or no drive letter assigned to the mounted virtual drive.')

def parse_pwsh_ISO_operation_output(stdout: str):
    while stdout.startswith('\r\n'):
            stdout = stdout.removeprefix('\r\n')
    while stdout.endswith('\r\n'):
        stdout = stdout.removesuffix('\r\n')
    lines = stdout.split('\r\n')
    ISO_info = {}
    for line in lines:
        split = line.split(' : ')
        key = split[0].strip()
        value = pwsh.convert_from_string(split[1].strip())
        ISO_info[key] = value
    return ISO_info

def mount(ISO_path: str):
    """Mount an ISO file to a virtual drive.

    Args:
        ISO_path (str): the path to the ISO file to mount.

    Raises:
        ISOMountError: if an error happens while mounting the provided ISO, this error will be raised.

    Returns:
        dict: the mounted ISO's data.
    """
    info = pwsh.run(f'Mount-DiskImage -ImagePath "{ISO_path}"')
    if info.returncode != 0:
        raise ISOMountError(info.stderr.decode('utf-8'))
    else:
        stdout = info.stdout.decode('utf-8')
        return parse_pwsh_ISO_operation_output(stdout)

def dismount(ISO_path: str):
    """Dismount an ISO file from a virtual drive.

    Args:
        ISO_path (str): the path to the ISO file to dismount.

    Raises:
        ISODismountError: if an error happens while dismounting the provided ISO, this error will be raised.

    Returns:
        dict: the dismounted ISO's data.
    """
    info = pwsh.run(f'Dismount-DiskImage -ImagePath "{ISO_path}"')
    if info.returncode != 0:
        raise ISODismountError(info.stderr.decode('utf-8'))
    else:
        stdout = info.stdout.decode('utf-8')
        return parse_pwsh_ISO_operation_output(stdout)

if __name__ == '__main__':
    from sys import argv, exit
    args = argv[1:]

    if len(args) != 1:
        print('need 1 arg (ISO)')
        exit(127)

    info = mount(args[0])
    print(info)
    disk = ISOInfoWrapper(info)
    print(disk.drive_letter)
    disk.dismount()

    #print(disk.dismount().mount().dismount())
