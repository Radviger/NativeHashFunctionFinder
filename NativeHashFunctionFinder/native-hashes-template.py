#---------------------------------------------------------------------
# This file was automatically generated by NativeHasFunctionFinder
#---------------------------------------------------------------------

import idaapi
from idc import *
# from binascii import unhexlify

##################################
### Override base address here ###
### only if auto-detect fails! ###
##################################
### The base address is where 
### the HEADER starts, 0x1000 
### bytes before the .text
### segment
##################################
# __idaBaseAddress = 0x140001000 - 0x1000 
##################################
__idaBaseAddress = 0


if __idaBaseAddress == 0:
    __ImageBase = LocByName("__ImageBase")
    if __ImageBase == BADADDR:
        print "You have no __ImageBase set in IDA."
    for seg in idautils.Segments():
        print "seg: %012x name: %s" % (seg, SegName(seg))
        if SegName(seg) == 'HEADER':
            __idaBaseAddress = seg
            break
        if SegName(seg) == '.text':
            __idaBaseAddress = seg - 0x1000
            print "No HEADER segment found, assuming BaseAddress is 0x%012x" % ( __idaBaseAddress )
            break

    if __ImageBase != __idaBaseAddress:
        print "Error: Start of HEADER segment 0x%012x does not match label __ImageBase 0x%012x, please adjust or remove __ImageBase label, or manually alter this file to set the correct base for your .text segment" % (__idaBaseAddress, __ImageBase)
        raise Exception("Your __ImageBase doesn't match what we think it should, please adjust script")

def PatchBytes(ea, replaceList):
    for i in range(len(replaceList)):
        if replaceList[i] != -1:
            idaapi.patch_byte(ea+i, replaceList[i])

def rebaseAddress(ea):
    return ea - __gtaBaseAddress + __idaBaseAddress

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
                print "%0x012x: Couldn't convert block into code even though it said we did" % ea
                return None
            return codeLen
        else:
            print "0x%012x: (head: 0x%012x) Couldn't convert block into code" % (ea, head)
            return None
    return length

def MakeNativeFunction(ea, name):
    ea = rebaseAddress(ea)
    if Byte(ea) == 0xe9:
        len = forceAsCode(ea, 5) # Natives are almost always a 5 byte JMP
    loc = 0
    while True:
        loc = LocByName(name)
        if loc == BADADDR:
            break
        if loc != ea:
            print "0x%012x: Removed existing name '%s'" % (loc, name)
        else:
            break
    MakeNameEx(loc, '', 0 )  # Remove any existing names that match
    if not MakeNameEx(ea, name, SN_NOWARN):
        # Try removing a previously existing name
        MakeNameEx( LocByName(name), '', 0 ) 
        if not MakeNameEx(ea, name, SN_NOWARN):
            print "0x%012x: *** Couldn't set name %s" % (ea, name)
    if not MakeFunction(ea, BADADDR):
        if not GetFunctionName(ea):
            print "0x%012x: *** Couldn't make area into function" % (ea)
        # SetFunctionEnd(ea, ea+5)

    codeMnem = GetMnem(ea)
    codeDisasm = GetDisasm(ea)
    extraMsg = ""
    if False:
        if codeMnem == 'jmp':
            forceAsCode(GetOperandValue(ea, 0), 8) # I think this might be causing sp-analysis breaks
            targetName = Name(GetOperandValue(ea, 0))
            targetMnem = GetMnem(GetOperandValue(ea, 0))
            targetDisasm = GetDisasm(GetOperandValue(ea, 0))
            if targetMnem == "retn":
                MakeNop(ea, 8) # 8 bit alignment
                extraMsg = " (replaced original JMP with RETN)"
            elif targetName is None:
                pass
            elif targetName.index('sub_') == 0:
                pass

            print "0x%012x: %-70s: %s -> %s%s" % (ea, name, codeDisasm, targetDisasm, extraMsg)
    else:
        print "0x%012x: %-70s: %s" % (ea, name, codeDisasm)
    
#---------------------------------------------------------------------

