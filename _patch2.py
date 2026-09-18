import struct, shutil, sys

SRC = "common/params_pyx.so"
BAK = "common/params_pyx.so.orig-prepatch"

b = bytearray(open(SRC, "rb").read())
orig = bytes(b)

def enc_adrp_add(pc, target):
    page = pc & ~0xFFF
    off = (target & ~0xFFF) - page
    imm = off >> 12
    if not (-0x800000 <= imm < 0x800000):
        raise Exception("adrp out of range: %x -> %x" % (pc, target))
    imm &= 0x1FFFFF
    adrp = 0x90000000 | (imm << 21) | (0 << 5) | 0
    lo = target & 0xFFF
    add = 0x91000000 | ((lo >> 12) << 22) | (lo & 0xFFF) << 10 | (0 << 5) | 0
    return adrp, add

def w32(off, v):
    b[off:off+4] = struct.pack("<I", v & 0xFFFFFFFF)

def put_code(base, insns):
    for i, (pc, v) in enumerate(insns):
        if pc != base + 4*i:
            raise Exception("pc mismatch")
        w32(base + 4*i, v)

NOP = 0xD503201F
MOV_X1_X1 = 0x2A0103E9

def build_match_key(base, lit_base):
    insns = []
    a = base
    def ins(v):
        insns.append((a, v)); a += 4
    ins(0xD100C3FF)          # sub sp,sp,#0x30
    ins(0xA9017BFD)          # stp x29,x30,[sp,#0x10]
    ins(0x910043FD)          # add x29,sp,#0x10
    ins(0x3B400020)          # uxtb x0,[x1]
    ins(0x531F7C08)          # lsr x8,x0,#1
    ins(0x0B080001)          # add w1,w0,w8   (size)
    ins(0x35000480)          # cbz w0,#a+100 (skip long)
    ins(0xF9401201)          # ldr x1,[x1,#8]
    ins(0xD503201F)          # nop
    ins(0xD503201F)          # nop
    ins(0xD503201F)          # nop
    ins(0xD503201F)          # nop
    # table loop start (a+80)
    ins(0x11000514)          # mov w4,#0
    a_start = a
    # loop: load len
    ins(0xB9400818)          # ldr w8,[x4]
    ins(0x6B01011F)          # cmp w8,w1
    ins(0x54000201)          # b.ne #a+32 (next)
    # len ok: compare bytes at a+16
    ins(0x11000519)          # mov w9,#0
    a_c0 = a
    ins(0x39400518)          # ldrb w8,[x5],#1
    ins(0x39400529)          # ldrb w9,[x1],#1
    ins(0x6B08011F)          # cmp w8,w9
    ins(0x54000041)          # b.ne #a+8 (end_no)
    ins(0x7100051F)          # subs w9,w9,#0
    ins(0x54000141)          # b.ne #a+20 (end_no)
    ins(0x11000519)          # mov w9,#0
    a_c1 = a
    ins(0x39400518)          # ldrb w8,[x5],#1
    ins(0x39400529)          # ldrb w9,[x1],#1
    ins(0x6B08011F)          # cmp w8,w9
    ins(0x54000041)          # b.ne #a+8 (end_no)
    ins(0x7100051F)          # subs w9,w9,#0
    ins(0x54000141)          # b.ne #a+20 (end_no)
    # end_no at a+48 (fallthrough)
    ins(0x14000000)          # b -> next (fixup)
    ins(0x52800020)          # mov w0,#0
    a_next = a
    ins(0x91002514)          # add x4,x4,#0x8
    ins(0x11000528)          # mov w8,#1
    ins(0x6B04011F)          # cmp w8,w4
    ins(0x540001C1)          # b.ne #a_start (fixup)
    ins(0x52800020)          # mov w0,#0
    a_end = a
    ins(0xA9417BFD)          # ldp x29,x30,[sp,#0x10]
    ins(0x9100C3FF)          # add sp,sp,#0x30
    ins(0xC00000C0)          # ret
    # fixups: b at a+48 (end_no) -> a_next
    delta = (a_next - (a_end - 20)) // 4
    # recompute: end_no index = (a_end-20 - base)//4
    idx_endno = (a_end - 20 - base) // 4
    delta = (a_next - (base + 4*idx_endno)) // 4
    insns[idx_endno] = (base + 4*idx_endno, 0x14000000 | (delta & 0x3FFFF))
    idx_next = (a_next - base) // 4
    delta = (a_start - (base + 4*idx_next)) // 4
    insns[idx_next] = (base + 4*idx_next, 0x14000000 | (delta & 0x3FFFF))
    # c0/c1 literal loads (x5 absolute)
    for idx, lit_va in [(a_c0 - base)//4, (a_c1 - base)//4]:
        adrp_v, add_v = enc_adrp_add(base + 4*idx, lit_va)
        insns[idx] = (base + 4*idx, adrp_v)
        # next slot must be add x5,x5,#imm -- but we already wrote ldrb there.
        # Instead: emit adr at idx, add at idx+? We need a free slot after each c0/c1.
        # We reserved 4 nops after the long-string branch; use them as add slots.
    return insns, a_end

print("stage1: check layout constants")
GAP = 0x270A0
CHK = 0x28EB0
KEYS = [
    b"dp_cam_decel",
    b"dp_cam_decel_mode",
    b"dp_cam_decel_start",
    b"dp_cam_decel_end",
    b"dp_cam_decel_bump_dist",
    b"dp_cam_decel_bump_speed",
    b"dp_cam_decel_safety_factor",
]
lit_base = GAP + 0x104
lits = []
off = lit_base
for k in KEYS:
    lits.append((k, off))
    off += len(k) + 2
print("lits end", hex(off), "gap end", hex(GAP + 0x1000))
print("OK constants")
