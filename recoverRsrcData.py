import zlib
import os
import logging
import SocketServer
import sys
import glob

BLOCK_SIZE = 1024

def findStart(file):
    import zlib
    f = open(file+'/..namedfork/rsrc','rb')
    BLOCK_SIZE = 128000
    d = f.read(BLOCK_SIZE)
    cont = True
    s = 0
    while cont:
        try:
            decompressed  = zlib.decompress(d[s:])
            cont = False
        except:
            s = s+1
            if s> BLOCK_SIZE:
                s = -1
                cont = False
    return s
    f.close()

def getRsrc(filename):
    output = open(filename+'.rsrc','wb')
    with open(filename+'/..namedfork/rsrc','rb') as input:
        fsize = os.fstat(input.fileno()).st_size
        while True:            
            to_go = fsize - input.tell()
            block = input.read(to_go > BLOCK_SIZE and BLOCK_SIZE or to_go)
            if len(block):
                output.write(block)

def readFile(filename):
    seek = findStart(filename)
    if seek == -1:
        print "%s does not have recoverable data in resource fork" % filename
        return
    with open(filename+'/..namedfork/rsrc','rb') as input:
        fsize = os.fstat(input.fileno()).st_size-50
        input.seek(seek)
        while True:            
            to_go = fsize - input.tell()
            block = input.read(to_go > BLOCK_SIZE and BLOCK_SIZE or to_go)
            if len(block):
                yield block
            else:
                break

def recoverFile(filename,output_file):
    output = open(output_file,'wb')
    decompressor = zlib.decompressobj()
    unused = ''
    for response in readFile(filename):
        if not response:
            break
        to_decompress = decompressor.unconsumed_tail + unused + response
        unused = ''
        while to_decompress:
            try:
                decompressed = decompressor.decompress(to_decompress)
            except:
                print "%s couldn't be decompressed" % filename
                return
            if decompressed:
                output.write(decompressed)
                to_decompress = decompressor.unconsumed_tail
                if decompressor.unused_data:
                    unused = decompressor.unused_data
                    remainder = decompressor.flush()
                    output.write(remainder)
                    decompressor = zlib.decompressobj()
            else:
                to_decompress = None
    remainder = decompressor.flush()
    if remainder:
        output.write(remainder)

""" Recover data from resource fork """
""" usage: python rescueRsrcData.py filename """
""" Grabs resource fork of HFS, runs contents through zlib inflate """
if __name__ == '__main__':
    requested_file = sys.argv[1]
    output_file = os.path.expanduser('~')+'/Desktop/'+os.path.basename(requested_file)
    recoverFile(requested_file,output_file)
