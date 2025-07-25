import ctypes
import ctypes.wintypes

# 先定义机器码
rdtsc_code = bytes([
    0x0F, 0x31,                         # rdtsc
    0x48, 0xC1, 0xE2, 0x20,             # shl rdx, 32
    0x48, 0x0B, 0xC2,                   # or rax, rdx
    0xC3                                # ret
])

PAGE_EXECUTE_READWRITE = 0x40
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000

# 申请可执行内存
VirtualAlloc = ctypes.windll.kernel32.VirtualAlloc
VirtualAlloc.restype = ctypes.c_void_p
ptr = VirtualAlloc(None, len(rdtsc_code), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
if not ptr:
    raise MemoryError("VirtualAlloc failed")

# 写入机器码
ctypes.memmove(ptr, rdtsc_code, len(rdtsc_code))

# 定义函数类型并调用
FUNC_TYPE = ctypes.CFUNCTYPE(ctypes.c_uint64)
rdtsc_func = FUNC_TYPE(ptr)

def rdtsc():
    return rdtsc_func()
