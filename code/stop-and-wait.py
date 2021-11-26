import socket
import argparse
import signal
import sys
import logging as log
import time
import random

RED = '\x1b[31;21m'
YELLOW = "\x1b[33;21m"
RESET = '\x1b[0m'
    

class SW:
    def __init__(self, bs, rtt=0, plr=0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = ('0.0.0.0', 0)
        self.bs = 0
        self.ACK = 'ACK'
        self.plr = plr
        self.rtt = rtt
    def send_packet(self, pckt):
        log.debug(f'Sending packet to {self.addr}')
        if self.rtt: time.sleep(self.rtt / 2.)
        if random.random() > self.plr:
            log.debug(f'{RED}Packet lost{RESET}')
            self.sock.sendto(pckt, self.addr)
    def recv_packet(self):
        packet, self.addr = self.sock.recvfrom(self.bs)
        log.debug(f'{YELLOW}Packet received from {self.addr}{RESET}')
        return packet
    def mk_packet(self):
        return ''.join(['1'] * self.bs).encode()

class Sender(SW):
    def __init__(self, ip, port, timeout, bs, counter, rtt=0, plr=0):
        super().__init__(bs=bs, rtt=rtt, plr=plr)
        self.addr = (ip, port)
        self.sock.settimeout(timeout)
        self.counter = counter
    def send_recv(self):
        self.send_packet(self.mk_packet())
        try: 
            ack = self.recv_packet()
        except socket.timeout as to: 
            log.debug('Timeout')
            return False
        self.counter -= 1
        return True
    def run(self):
        while self.counter:
            self.send_recv()
        log.info(f'Transmission finished. Exit.')

class Receiver(SW):
    def __init__(self, bs, port, rtt=0, plr=0):
        super().__init__(bs=bs, rtt=rtt, plr=plr)
        self.addr_local = ('0.0.0.0', port)
        self.sock.bind(self.addr_local)
    def run(self):
        log.info(f'Waiting connection on port {self.addr_local[1]}')
        while True: 
            pckt = self.recv_packet()
            self.send_packet(self.ACK.encode())

    
def signal_handler(*args):
    log.info('You pressed Ctrl+C! Exit...\n')
    sys.exit(0)

parser = argparse.ArgumentParser(prog='Stop and Wait')
mode = parser.add_mutually_exclusive_group(required=True)
mode.add_argument("-s", "--sender",        action='store_true', help="the program run as a sender")
mode.add_argument("-r", "--receiver",      action='store_true', help="the program run as a receiver")

parser.add_argument("-p", "--receiverport", type=int, help="specify the receiver port")
parser.add_argument("-ip", "--sendaddress",   type=str, help="specify the address to send")

parser.add_argument("-c", "--counter",       type=int, help="specify the number of packets to send", default=1000)
parser.add_argument("-t", "--timeout",       type=float, help="specify timeout", default=0.1)
parser.add_argument("-fs", "--framesize",    type=int, help="specify the size of the frame in bytes", default=1472)
parser.add_argument('-v', '--verbosity', action="count", help="increase output verbosity (e.g., -vv is more than -v)")


parser.add_argument("-rtt", "--rtt",       type=float, help="specify round trip time delay", default=0)
parser.add_argument("-plr", "--plr",       type=float, help="specify packet loss rate", default=0)

log_levels = {0 : log.NOTSET, 1 : log.INFO, 2 : log.DEBUG}


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler) # catch SIGIN with signal_handler
    args = parser.parse_args()
    log.basicConfig(format="%(levelname)s: %(message)s", level = log_levels.get(args.verbosity, log.ERROR))
    if args.sender:
        packet_handler = Sender(args.sendaddress, args.receiverport, args.timeout, args.framesize, args.counter, args.rtt, args.plr)
    if args.receiver:
        packet_handler = Receiver(args.framesize, args.receiverport, args.rtt, args.plr)
    t1 = time.time()
    packet_handler.run()
    t2 = time.time()
    print(t2 - t1)








