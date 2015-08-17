#!/usr/bin/env python

__description__ = 'Translate bytes according to a Python expression'
__author__ = 'Didier Stevens'
__version__ = '2.0.0'
__date__ = '2014/02/27'

"""

Source code put in public domain by Didier Stevens, no Copyright
https://DidierStevens.com
Use at your own risk

No input validation (neither output) is performed by this program: it contains injection vulnerabilities

Developed with Python 2.7, tested with 2.7 and 3.3

History:
  2007/08/20: start
  2014/02/24: rewrite
  2014/02/27: manual

Todo:
"""

import optparse
import sys
import os
import textwrap

def PrintManual():
    manual = '''
Manual:

Translate.py is a Python script to perform bitwise operations on files (like XOR, ROL/ROR, ...). You specify the bitwise operation to perform as a Python expression, and pass it as a command-line argument.

translate.py malware -o malware.decoded "byte ^ 0x10"
This will read file malware, perform XOR 0x10 on each byte (this is, expressed in Python: byte ^ 0x10), and write the result to file malware.decoded.

byte is a variable containing the current byte from the input file. Your expression has to evaluate to the modified byte. For complex manipulation, you can define your own functions in a script file and load this with translate.py, like this:

translate.py malware -o malware.decoded "Process(byte)" process.py
process.py must contain the definition of function Process. Function Process must return the modified byte.

Another variable is also available: position. This variable contains the position of the current byte in the input file, starting from 0.

If only part of the file has to be manipulated, while leaving the rest unchanged, you can do it like this:

    def Process(byte):
        if position >= 0x10 and position < 0x20:
            return byte ^ 0x10
        else:
            return byte

This example will perform an XOR 0x10 operation from the 17th byte till the 32nd byte included. All other bytes remain unchanged.

Because Python as built-in shift operators (<< and >>) but no rotate operators, I've defined 2 rotate functions that operate on a byte: rol (rotate left) and ror (rotate right). They accept 2 arguments: the byte to rotate and the number of bit positions to rotate. For example, rol(0x01, 2) gives 0x04.

translate.py malware -o malware.decoded "rol(byte, 2)"

Another function I defined is IFF (the IF Function): IFF(expression, valueTrue, valueFalse). This function allows you to write conditional code without an if statement. When expression evaluates to True, IFF returns valueTrue, otherwise it returns valueFalse.

translate.py malware -o malware.decoded "IFF(position >= 0x10 and position < 0x20, byte ^ 0x10, byte)"
'''
    for line in manual.split('\n'):
        print(textwrap.fill(line))

def rol(byte, count):
    return (byte << count | byte >> (8- count)) & 0xFF

def ror(byte, count):
    return (byte >> count | byte << (8- count)) & 0xFF

# CIC: Call If Callable
def CIC(expression):
    if callable(expression):
        return expression()
    else:
        return expression

# IFF: IF Function
def IFF(expression, valueTrue, valueFalse):
    if expression:
        return CIC(valueTrue)
    else:
        return CIC(valueFalse)

#Convert String To Bytes If Python 3
def CS2BIP3(string):
    if sys.version_info[0] > 2:
        return bytes([ord(x) for x in string])
    else:
        return string

def Transform(fIn, fOut, commandPython):
    position = 0
    while True:
        inbyte = fIn.read(1)
        if not inbyte:
            break
        byte = ord(inbyte)
        outbyte = eval(commandPython)
        fOut.write(CS2BIP3(chr(outbyte)))
        position += 1
    if fIn != sys.stdin:
        fIn.close()
    if fOut != sys.stdout:
        fOut.close()

def Translate(filenameInput, commandPython, options):
    if filenameInput == '':
        if sys.platform == 'win32':
            import msvcrt
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        fIn = sys.stdin
    else:
        fIn = open(filenameInput, 'rb')

    if options.output == '':
        if sys.platform == 'win32':
            import msvcrt
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
        fOut = sys.stdout
    else:
        fOut = open(options.output, 'wb')

    if options.script != '':
        execfile(options.script)

    Transform(fIn, fOut, commandPython)

def Main():
    moredesc = '''

Example: translate.py -o svchost.exe.dec svchost.exe 'byte ^ 0x10'
"byte" is the current byte in the file, 'byte ^ 0x10' does an X0R 0x10
Extra functions:
  rol(byte, count)
  ror(byte, count)
  IFF(expression, valueTrue, valueFalse)
Variable "position" is an index into the input file, starting at 0

Source code put in the public domain by Didier Stevens, no Copyright
Use at your own risk
https://DidierStevens.com'''

    oParser = optparse.OptionParser(usage='usage: %prog [options] [file-in] [file-out] command [script]\n' + __description__ + moredesc, version='%prog ' + __version__)
    oParser.add_option('-o', '--output', default='', help='Output file (default is stdout)')
    oParser.add_option('-s', '--script', default='', help='Script with definitions to include')
    oParser.add_option('-m', '--man', action='store_true', default=False, help='print manual')
    (options, args) = oParser.parse_args()

    if options.man:
        oParser.print_help()
        PrintManual()
        return

    if len(args) == 0 or len(args) > 4:
        oParser.print_help()
    elif len(args) == 1:
        Translate('', args[0], options)
    elif len(args) == 2:
        Translate(args[0], args[1], options)
    elif len(args) == 3:
        options.output = args[1]
        Translate(args[0], args[2], options)
    elif len(args) == 4:
        options.output = args[1]
        options.script = args[3]
        Translate(args[0], args[2], options)

if __name__ == '__main__':
    Main()
