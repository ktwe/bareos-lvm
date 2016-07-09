**Warning:** This plugin comes with no warranty. It is in a very early stage of development and can cause data loss. Do not use it in production. 

# Bareos LVM Plugin
This filedaemon plugin uses snapshots to backup LVM volumes. The process is as follows:

* Create a snapshot of the specified volume.
* Stream snapshot to Bareos-fd.
* Return original volume name to Bareos for easier restore.
* Delete snapshot.

Backup of volumes is done sequentially so only one volume snapshot exists at the same time. By default a snapshot with 10% of the original volumes size is created.

# Install
* Install `bareos-filedaemon-python-plugin`.
* Copy `lvm_tools.py` and `bareos-fd-lvm.py` to `/usr/lib/bareos/plugins` on the filedaemon host.
* Activate Plugins in your `bareos-fd.conf` (look for `Plugin Directory` directive).

# Usage
Add the following to your Fileset and change the `volume_group` parameter:
```
Plugin = "python:module_path=/usr/lib/bareos/plugins:module_name=bareos-fd-lvm:volume_group=vg-data"
```

**Note:** Using a fast compression algorithm like LZO is highly recommended.