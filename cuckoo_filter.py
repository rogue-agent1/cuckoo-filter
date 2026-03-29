#!/usr/bin/env python3
"""Cuckoo filter — space-efficient probabilistic set with deletion."""
import sys, hashlib, random

class CuckooFilter:
    def __init__(self, capacity=1024, bucket_size=4, fp_size=8, max_kicks=500):
        self.capacity, self.bucket_size = capacity, bucket_size
        self.fp_size, self.max_kicks = fp_size, max_kicks
        self.buckets = [[] for _ in range(capacity)]
        self.count = 0
    def _fingerprint(self, item):
        return int(hashlib.md5(item.encode()).hexdigest(), 16) % (1 << self.fp_size) or 1
    def _hash(self, item):
        return int(hashlib.sha256(item.encode()).hexdigest(), 16) % self.capacity
    def _alt_index(self, i, fp):
        return (i ^ int(hashlib.md5(str(fp).encode()).hexdigest(), 16)) % self.capacity
    def insert(self, item):
        fp = self._fingerprint(item)
        i1 = self._hash(item); i2 = self._alt_index(i1, fp)
        for i in (i1, i2):
            if len(self.buckets[i]) < self.bucket_size:
                self.buckets[i].append(fp); self.count += 1; return True
        i = random.choice([i1, i2])
        for _ in range(self.max_kicks):
            j = random.randrange(len(self.buckets[i]))
            fp, self.buckets[i][j] = self.buckets[i][j], fp
            i = self._alt_index(i, fp)
            if len(self.buckets[i]) < self.bucket_size:
                self.buckets[i].append(fp); self.count += 1; return True
        return False
    def lookup(self, item):
        fp = self._fingerprint(item)
        i1 = self._hash(item); i2 = self._alt_index(i1, fp)
        return fp in self.buckets[i1] or fp in self.buckets[i2]
    def delete(self, item):
        fp = self._fingerprint(item)
        i1 = self._hash(item); i2 = self._alt_index(i1, fp)
        for i in (i1, i2):
            if fp in self.buckets[i]:
                self.buckets[i].remove(fp); self.count -= 1; return True
        return False

def main():
    cf = CuckooFilter()
    for w in ["apple","banana","cherry"]: cf.insert(w)
    for w in ["apple","banana","cherry","date"]:
        print(f"{w}: {cf.lookup(w)}")
    cf.delete("banana"); print(f"After delete banana: {cf.lookup('banana')}")

if __name__ == "__main__": main()
