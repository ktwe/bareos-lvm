import subprocess

def get_all_volumes_in_volume_group(volume_group):
	"""
	Returns a list of volumes in the given volume_group. Volumes are returned as absolute /dev/... pathes.
	"""

	command = ['/sbin/lvdisplay', '-c', volume_group]

	# get logical volumes
	logical_volumes = subprocess.check_output(command)

	# output is one volume per line
	logical_volumes = logical_volumes.split('\n')

	# remove last empty line
	logical_volumes = logical_volumes[0:-1]

	# remove whitespaces
	logical_volumes = map(lambda x: x.strip(), logical_volumes)

	# data is seperated by : - first position is absolute path /dev/...
	logical_volumes = map(lambda x: x.split(':')[0], logical_volumes)

	return logical_volumes

def create_lvm_snapshot(volume, snapshot_size=0.10, suffix='backup'):
	"""
	Creates a snapshot of a given volume.
	snapshot_size sets the size of the snapshot in percent of the original volume.
	suffix is added to the original volume name to create a snapshot name.
	"""

	# get current size of volume
	get_size_command = ['/sbin/lvs', '-o', 'LV_SIZE', '--noheadings', '--nosuffix', '--units', 'B', volume]

	size = subprocess.check_output(get_size_command)
	
	# remove unnecessary linebreaks
	size = size.split('\n')
	size = size[0]

	# remove whitespaces and convert to int
	size = int(size.strip())

	# calculate snapshot size based on snapshot_size
	abs_snapshot_size = snapshot_size * size
	abs_snapshot_size = int(abs_snapshot_size)

	# snapshot size must be a multiple of 512
	abs_snapshot_size = abs_snapshot_size - (abs_snapshot_size % 512)
	abs_snapshot_size = '{}B'.format(abs_snapshot_size)

	# last part of volumes path is the volume_name
	volume_name = volume.split('/')[-1]
	snapshot_name = '{}-{}'.format(volume_name, suffix)

	create_snapshot_command = ['/sbin/lvcreate', '-L', abs_snapshot_size, '-n', snapshot_name, '-s', volume]

	subprocess.check_output(create_snapshot_command)

	# return tupple (snapshot_path, volume_size)
	return ('{}/{}'.format('/'.join(volume.split('/')[0:-1]), snapshot_name), size)

def delete_lvm_snapshot(volume):
	"""
	Deletes an LVM volume.
	"""
	
	delete_command = ['/sbin/lvremove', '--force', volume]

	subprocess.check_output(delete_command)