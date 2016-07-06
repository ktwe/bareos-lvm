import subprocess

def get_all_volumes_in_volume_group(volume_group):
	command = ['/sbin/lvdisplay', '-c', volume_group]

	logical_volumes = subprocess.check_output(command)
	logical_volumes = logical_volumes.split('\n')
	logical_volumes = logical_volumes[0:-1]

	logical_volumes = map(lambda x: x.strip(), logical_volumes)
	logical_volumes = map(lambda x: x.split(':')[0], logical_volumes)

	return logical_volumes

def create_lvm_snapshot(volume, snapshot_size=0.10, suffix='backup'):
	#lvs -o LV_SIZE --noheadings --nosuffix /dev/test/volume-12345 --units B
	
	get_size_command = ['/sbin/lvs', '-o', 'LV_SIZE', '--noheadings', '--nosuffix', '--units', 'B', volume]

	size = subprocess.check_output(get_size_command)
	size = size.split('\n')
	size = size[0]
	size = int(size.strip())

	abs_snapshot_size = snapshot_size * size
	abs_snapshot_size = int(abs_snapshot_size)
	abs_snapshot_size = abs_snapshot_size - (abs_snapshot_size % 512)
	abs_snapshot_size = '{}B'.format(abs_snapshot_size)

	volume_name = volume.split('/')[-1]
	snapshot_name = '{}-{}'.format(volume_name, suffix)

	create_snapshot_command = ['/sbin/lvcreate', '-L', abs_snapshot_size, '-n', snapshot_name, '-s', volume]

	subprocess.check_output(create_snapshot_command)

	return ('{}/{}'.format('/'.join(volume.split('/')[0:-1]), snapshot_name), size)

def delete_lvm_snapshot(volume):
	delete_command = ['/sbin/lvremove', '--force', volume]

	subprocess.check_output(delete_command)