import iso
from sys import argv, exit
args = argv[1:]

if len(args) != 2:
    print('Expected 2 args (ISO, destination)')
    exit(127)

print('Mounting ISO...')
info = iso.mount(args[0])
print('Wrapping ISO to Python object...')
wrapper = iso.ISOInfoWrapper(info)
print('Copying ISO content...')
wrapper.copy(args[1])
print('Dismounting ISO...')
wrapper.dismount()
