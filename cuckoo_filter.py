#!/usr/bin/env python3
"""Cuckoo Filter — space-efficient probabilistic set with deletion support."""
import hashlib, random, sys

class CuckooFilter:
    def __init__(self, capacity=1024, bucket_size=4, max_kicks=500):
        self.capacity, self.bucket_size = capacity, bucket_size
        self.max_kicks = max_kicks
        self.buckets = [[] for _ in range(capacity)]
        self.count = 0
    def _fingerprint(self, item):
        return int(hashlib.md5(str(item).encode()).hexdigest()[:4], 16) | 1
    def _hash(self, item):
        return int(hashlib.sha256(str(item).encode()).hexdigest(), 16) % self.capacity
    def _alt_index(self, idx, fp):
        return (idx ^ int(hashlib.sha256(str(fp).encode()).hexdigest(), 16)) % self.capacity
    def insert(self, item):
        fp = self._fingerprint(item)
        i1 = self._hash(item)
        i2 = self._alt_index(i1, fp)
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
        i1 = self._hash(item)
        return fp in self.buckets[i1] or fp in self.buckets[self._alt_index(i1, fp)]
    def delete(self, item):
        fp = self._fingerprint(item)
        i1 = self._hash(item)
        for i in (i1, self._alt_index(i1, fp)):
            if fp in self.buckets[i]:
                self.buckets[i].remove(fp); self.count -= 1; return True
        return False

if __name__ == "__main__":
    cf = CuckooFilter(64, 4)
    for i in range(20): cf.insert(f"item-{i}")
    print(f"Count: {cf.count}")
    print(f"Lookup item-5: {cf.lookup('item-5')}")
    cf.delete("item-5")
    print(f"After delete item-5: {cf.lookup('item-5')}")
    print(f"Lookup item-99: {cf.lookup('item-99')}")
