"""Platform process lifetime: POSIX groups and Windows jobs, never a shell."""
import os
import signal
import subprocess
import sys
import psutil


class WindowsJob:
    """Assign suspended children before they can spawn descendants; close kills the tree."""
    def __init__(self, memory_limit=None):
        import ctypes as c
        from ctypes import wintypes as w

        class Basic(c.Structure):
            _fields_ = [('ProcessTime', c.c_longlong), ('JobTime', c.c_longlong),
                        ('Flags', w.DWORD), ('MinWorkingSet', c.c_size_t),
                        ('MaxWorkingSet', c.c_size_t), ('ActiveProcesses', w.DWORD),
                        ('Affinity', c.c_size_t), ('Priority', w.DWORD), ('Scheduling', w.DWORD)]

        class IO(c.Structure):
            _fields_ = [(name, c.c_ulonglong) for name in
                        ['ReadOps', 'WriteOps', 'OtherOps', 'ReadBytes', 'WriteBytes', 'OtherBytes']]

        class Extended(c.Structure):
            _fields_ = [('Basic', Basic), ('IO', IO), ('ProcessMemory', c.c_size_t),
                        ('JobMemory', c.c_size_t), ('PeakProcessMemory', c.c_size_t),
                        ('PeakJobMemory', c.c_size_t)]

        self.api = c.WinDLL('kernel32', use_last_error=True)
        self.api.CreateJobObjectW.argtypes = [c.c_void_p, w.LPCWSTR]
        self.api.CreateJobObjectW.restype = w.HANDLE
        self.api.SetInformationJobObject.argtypes = [w.HANDLE, c.c_int, c.c_void_p, w.DWORD]
        self.api.SetInformationJobObject.restype = w.BOOL
        self.api.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
        self.api.AssignProcessToJobObject.restype = w.BOOL
        self.api.CloseHandle.argtypes = [w.HANDLE]
        self.api.CloseHandle.restype = w.BOOL
        self.handle = self.api.CreateJobObjectW(None, None)
        if not self.handle:
            raise c.WinError(c.get_last_error())
        info = Extended()
        info.Basic.Flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if memory_limit:
            info.Basic.Flags |= 0x200 | 0x4  # job memory and total user CPU time
            info.JobMemory = memory_limit
            info.Basic.JobTime = 35 * 10_000_000
        if not self.api.SetInformationJobObject(self.handle, 9, c.byref(info), c.sizeof(info)):
            failure = c.WinError(c.get_last_error())
            self.close()
            raise failure

    def assign(self, process):
        import ctypes
        # Popen retains the native process handle for its full lifetime on Windows.
        if not self.api.AssignProcessToJobObject(self.handle, int(process._handle)):
            raise ctypes.WinError(ctypes.get_last_error())

    def close(self):
        if self.handle:
            self.api.CloseHandle(self.handle)
            self.handle = None


def start(args, *, memory_limit=None, **kwargs):
    if sys.platform != 'win32':
        return subprocess.Popen(args, start_new_session=True, **kwargs), None
    job = WindowsJob(memory_limit)
    process = None
    try:
        # Hold the initial thread until job membership is established (no spawn race).
        process = subprocess.Popen(args, creationflags=0x4 | subprocess.CREATE_NO_WINDOW, **kwargs)
        job.assign(process)
        psutil.Process(process.pid).resume()
        return process, job
    except BaseException:
        job.close()
        if process is not None:
            if process.poll() is None:
                process.kill()
            process.wait()
        raise


def terminate(process, job=None):
    if job is not None:
        job.close()  # Also kills descendants after their original parent has exited.
        process.wait()
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=.3)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait()
