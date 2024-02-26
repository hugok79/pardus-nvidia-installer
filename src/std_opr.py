import os
import gi
import dbus
import subprocess

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk


def on_process_stdout(src, cond, self):
    if cond == GLib.IO_HUP:
        return False
    line = src.readline()
    if "dlstatus" in line or "pmstatus" in line:
        splits = line.split(":")
        prc = float(splits[2])
        txt = splits[3]
        prg_frac = float(prc / 100)
        prog_txt = f"Status %{prc:.2f} :: {txt}"
        self.ui_status_progressbar.set_text(prog_txt)
        self.ui_status_progressbar.set_fraction(prg_frac)
    return True


def on_process_stderr(src, cond, ui_obj):
    if cond == GLib.IO_HUP:
        return False
    line = src.readline()
    return True


def on_process_stdext(pid, stat, self):
    print(stat)
    self.ui_status_progressbar.set_fraction(1)
    if stat == 0:
        self.ui_status_progressbar.set_text("Operation completed successfully")
        if self.apt_opr != "update":
            if self.ui_confirm_dialog:
                dlg_res = self.ui_confirm_dialog.run()
                if dlg_res == Gtk.ResponseType.OK:
                    subprocess.call(
                    [
                        "dbus-send",
                        "--system",
                        "--print-reply",
                        "--dest=org.freedesktop.login1",
                        "/org/freedesktop/login1",
                        "org.freedesktop.login1.Manager.Reboot",
                        "boolean:true",
                    ]
                 )
                elif dlg_res == Gtk.ResponseType.CANCEL:
                    pass
            self.ui_confirm_dialog.destroy()
        self.create_gpu_drivers()
    else:
        self.ui_status_progressbar.set_text("An error occured.")
        return False
    self.check_source()
    self.ui_main_window.set_sensitive(True)
