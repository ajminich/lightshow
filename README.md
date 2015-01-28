# lightshow
A simple Raspberry Pi project to control GPIOs over a REST API.

## Setup

### Serial Connection
Follow http://elinux.org/RPi_Serial_Connection for directions on setting up a
serial connection over USB.

### Remote Filesystem
Follow https://medium.com/dev-tricks/mount-a-remote-filesystem-with-sshfs-8a37e85b39ee
for directions on setting up a remote filesystem.

```
mkdir remote_home
sshfs me@www.myhost.com:/home/me/ remote_home
ls -l remote_home/
````

To unmount simply:

```
umount remote_home
```
