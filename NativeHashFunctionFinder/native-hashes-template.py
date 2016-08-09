#---------------------------------------------------------------------
# This file was automatically generated by NativeHasFunctionFinder
#---------------------------------------------------------------------

import idaapi
from idc import *
from binascii import unhexlify

__idaBaseAddress = Segments().next()

def PatchBytes(ea, replaceList):
    for i in range(len(replaceList)):
        if replaceList[i] != -1:
            idaapi.patch_byte(ea+i, replaceList[i])

def rebaseAddress(ea):
    return ea #  - __gtaBaseAddress + __idaBaseAddress

def forceAsCode(ea, length):
    if not isCode(GetFlags(ea)):
        head = ItemHead(ea)
        head = ea if (head > 1<<31 or not head) else head
        if MakeUnknown(head, length, 0) == False:
            print "Couldn't make unknown at  0x%012x" % ea
            return None
        codeLen = MakeCode(ea)

        if codeLen:
            if not isCode(GetFlags(ea)):
                print "Couldn't convert block into code even though it said we did 0x%012x" % ea
                return None
            return codeLen
        else:
            print "Couldn't convert block into code at 0x%012x (head: 0x%012x)" % (ea, head)
            return None
    return length

def MakeNativeFunction(ea, name):
    ea = rebaseAddress(ea)
    len = forceAsCode(ea, 5)
    MakeNameEx( LocByName(name), '', 0 )
    if not MakeNameEx(ea, name, SN_NOWARN):
        MakeNameEx( LocByName(name), '', 0 )
        if not MakeNameEx(ea, name, SN_NOWARN):
            print "%012x: *** Couldn't set name %s" % (ea, name)
    if not MakeFunction(ea, BADADDR):
        if not GetFunctionName(ea):
            print "%012x: *** Couldn't make area into function" % (ea)
        # SetFunctionEnd(ea, ea+5)

    codeMnem = GetMnem(ea)
    codeDisasm = GetDisasm(ea)
    if codeMnem == 'jmp':
        forceAsCode(GetOperandValue(ea, 0), 8)
        targetMnem = GetMnem(GetOperandValue(ea, 0))
        targetDisasm = GetDisasm(GetOperandValue(ea, 0))
        if targetMnem == "retn":
            MakeNop(ea, 8) # 8 bit alignment
            extraMsg = " (replaced original JMP with RETN)"
        else:
            extraMsg = ""

        print "%012x: %-70s: %s -> %s%s" % (ea, name, codeDisasm, targetDisasm, extraMsg)
    else:
        print "%012x: %-70s: %s" % (ea, name, codeDisasm)
    
#---------------------------------------------------------------------
