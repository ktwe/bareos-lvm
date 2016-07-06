# BAREOS - Backup Archiving REcovery Open Sourced
#
# Copyright (C) 2013-2014 Bareos GmbH & Co. KG
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of version three of the GNU Affero General Public
# License as published by the Free Software Foundation, which is
# listed in the file LICENSE.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
# Author: Marco van Wieringen
#
from bareosfd import *
from bareos_fd_consts import *
from io import open
from os import O_WRONLY, O_CREAT
from subprocess import CalledProcessError
import lvm_tools

def load_bareos_plugin(context, plugindef):
  DebugMessage(context, 100, "load_bareos_plugin called with param: " + plugindef + "\n");
  events = [];
  events.append(bEventType['bEventJobEnd']);
  events.append(bEventType['bEventEndBackupJob']);
  events.append(bEventType['bEventEndFileSet']);
  events.append(bEventType['bEventHandleBackupFile']);
  RegisterEvents(context, events);
  fdname = GetValue(context, bVariable['bVarFDName']);
  DebugMessage(context, 100, "FDName = " + fdname + "\n");
  workingdir = GetValue(context, bVariable['bVarWorkingDir']);
  DebugMessage(context, 100, "WorkingDir = " + workingdir + "\n");

  return bRCs['bRC_OK'];

def parse_plugin_definition(context, plugindef):
  global vg_to_backup, volumes;

  DebugMessage(context, 100, "parse_plugin_definition called with param: " + plugindef + "\n");
  vg_to_backup = "Unknown";
  plugin_options = plugindef.split(":");
  for current_option in plugin_options:
    key,sep,val = current_option.partition("=");
    if val == '':
      continue;

    elif key == 'module_path':
      continue;

    elif key == 'module_name':
      continue;

    elif key == 'volume_group':
      vg_to_backup = val;
      continue;

    else:
      DebugMessage(context, 100, "parse_plugin_definition unknown option " + key + " with value " + val + "\n");
      return bRCs['bRC_Error'];

  volumes = lvm_tools.get_all_volumes_in_volume_group(vg_to_backup)

  return bRCs['bRC_OK'];

def handle_plugin_event(context, event):
  if event == bEventType['bEventJobEnd']:
    DebugMessage(context, 100, "handle_plugin_event called with bEventJobEnd\n");

  elif event == bEventType['bEventEndBackupJob']:
    DebugMessage(context, 100, "handle_plugin_event called with bEventEndBackupJob\n");

  elif event == bEventType['bEventEndFileSet']:
    DebugMessage(context, 100, "handle_plugin_event called with bEventEndFileSet\n");

  else:
    DebugMessage(context, 100, "handle_plugin_event called with event " + str(event) + "\n");

  return bRCs['bRC_OK'];

def start_backup_file(context, savepkt):
  global snapshot

  DebugMessage(context, 100, "start_backup called\n");
  if vg_to_backup == 'Unknown':
    JobMessage(context, bJobMessageType['M_FATAL'], "No volume group specified in plugin definition to backup\n");
    return bRCs['bRC_Error'];

  volume = volumes.pop();

  JobMessage(context, bJobMessageType['M_INFO'], "Starting backup of " + volume + "\n");

  try:
    snapshot = lvm_tools.create_lvm_snapshot(volume)
    size = snapshot[1]
    snapshot = snapshot[0]
  except CalledProcessError as e:
    JobMessage(context, bJobMessageType['M_FATAL'], e.output);
    return bRCs['bRC_Error'];

  statp = StatPacket();
  statp.size = size
  savepkt.statp = statp
  savepkt.fname = volume
  savepkt.type = bFileType['FT_REG'];

  return bRCs['bRC_OK'];

def end_backup_file(context):
  DebugMessage(context, 100, "end_backup_file() entry point in Python called\n")

  try:
    lvm_tools.delete_lvm_snapshot(snapshot)
  except CalledProcessError as e:
    JobMessage(context, bJobMessageType['M_FATAL'], e.output);

  if volumes:
    return bRCs['bRC_More'];

  return bRCs['bRC_OK'];

def plugin_io(context, IOP):
  global file

  DebugMessage(context, 100, "plugin_io called with " + str(IOP) + "\n");

  FNAME = IOP.fname;
  if IOP.func == bIOPS['IO_OPEN']:
    try:
      if IOP.flags & (O_CREAT | O_WRONLY):
        file = open(FNAME, 'wb');
      else:
        file = open(snapshot, 'rb');
    except:
      IOP.status = -1;
      return bRCs['bRC_Error'];

    return bRCs['bRC_OK'];

  elif IOP.func == bIOPS['IO_CLOSE']:
    file.close();
    return bRCs['bRC_OK'];

  elif IOP.func == bIOPS['IO_SEEK']:
    return bRCs['bRC_OK'];

  elif IOP.func == bIOPS['IO_READ']:
    IOP.buf = bytearray(IOP.count);
    IOP.status = file.readinto(IOP.buf);
    IOP.io_errno = 0
    return bRCs['bRC_OK'];

  elif IOP.func == bIOPS['IO_WRITE']:
    IOP.status = file.write(IOP.buf);
    IOP.io_errno = 0
    return bRCs['bRC_OK'];

def start_restore_file(context, cmd):
  DebugMessage(context, 100, "start_restore_file() entry point in Python called with " + str(cmd) + "\n")
  return bRCs['bRC_OK'];

def end_restore_file(context):
  DebugMessage(context, 100, "end_restore_file() entry point in Python called\n")
  return bRCs['bRC_OK'];

def create_file(context, restorepkt):
  DebugMessage(context, 100, "create_file() entry point in Python called with " + str(restorepkt) + "\n")
  restorepkt.create_status = bCFs['CF_EXTRACT'];
  return bRCs['bRC_OK'];

def set_file_attributes(context, restorepkt):
  DebugMessage(context, 100, "set_file_attributes() entry point in Python called with " + str(restorepkt) + "\n")
  return bRCs['bRC_OK'];

def check_file(context, fname):
  DebugMessage(context, 100, "check_file() entry point in Python called with " + str(fname) + "\n")
  return bRCs['bRC_OK'];

def get_acl(context, acl):
  DebugMessage(context, 100, "get_acl() entry point in Python called with " + str(acl) + "\n")
  return bRCs['bRC_OK'];

def set_acl(context, acl):
  DebugMessage(context, 100, "set_acl() entry point in Python called with " + str(acl) + "\n")
  return bRCs['bRC_OK'];

def get_xattr(context, xattr):
  DebugMessage(context, 100, "get_xattr() entry point in Python called with " + str(xattr) + "\n")
  return bRCs['bRC_OK'];

def set_xattr(context, xattr):
  DebugMessage(context, 100, "set_xattr() entry point in Python called with " + str(xattr) + "\n")
  return bRCs['bRC_OK'];

def restore_object_data(context, restoreobject):
  DebugMessage(context, 100, "restore_object_data called with " + str(restoreobject) + "\n");
  return bRCs['bRC_OK'];

def handle_backup_file(context, savepkt):
  DebugMessage(context, 100, "handle_backup_file called with " + str(savepkt) + "\n");
  return bRCs['bRC_OK'];
