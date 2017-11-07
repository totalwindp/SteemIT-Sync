import json
import os
import time

import baseconvert

from contextlib import suppress
from steem.blockchain import Blockchain


def get_last_line(filename):
    if os.path.isfile(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'rb') as f:
            f.seek(-2, 2)
            while f.read(1) != b"\n":
                f.seek(-2, 1)
            return f.readline()


def get_previous_block_num(block):
    if not block:
        return -1

    if type(block) == bytes:
        block = block.decode('utf-8')

    if type(block) == str:
        block = json.loads(block)

    return int(block['previous'][:8], base=16)
    
def progress(local_blk, upstream_blk):
	#local_num = baseconvert.base(local_blk, 16, 10)
	#upstream_num = baseconvert.base(upstream_blk, 16, 10)
	
	#progress = (local_num / upstream_num) * 100
	progress = (local_blk / upstream_blk) * 100
	return progress
	


def run(filename):
    b = Blockchain()
    # automatically resume from where we left off
    # previous + last + 1
    start_block = get_previous_block_num(get_last_line(filename)) + 2
    upstream_blk = b.get_current_block()
    checkin_count = 0
    
    print("Our local block: {}".format(start_block))
    print("The Upstream block: {}".format(b.get_current_block_num()))
    print("Progress: {}%\n".format(progress(start_block, b.get_current_block_num())))
    
    with open(filename, 'a+') as file:
        checkin_ts = time.time()
        for block in b.stream_from(start_block=start_block, full_blocks=True):
            if checkin_ts+10 < time.time():
                pdone = progress(int(block['block_id'][:8], base=16), b.get_current_block_num())
                dl_rate = checkin_count / 10
                
                print("Rate: {}blk/sec, Progress: {}%".format(dl_rate, pdone))
                checkin_ts = time.time()
                checkin_count = 0
				
				
            file.write(json.dumps(block, sort_keys=True) + '\n')
            checkin_count += 1


if __name__ == '__main__':
    output_file = '/var/log/steem.blockchain.json'
    with suppress(KeyboardInterrupt):
        run(output_file)
