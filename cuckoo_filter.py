#!/usr/bin/env python3
"""Cuckoo filter — probabilistic set with deletion."""
import hashlib, random, sys

class CuckooFilter:
    def __init__(self, capacity=1024, bucket_size=4, fp_size=8):
        self.capacity = capacity
        self.bucket_size = bucket_size
        self.fp_size = fp_size
        self.buckets = [[] for _ in range(capacity)]
        self.count = 0
    def _fingerprint(self, item):
        h = hashlib.sha256(str(item).encode()).digest()
        return h[:self.fp_size]
    def _hash(self, item):
        return int(hashlib.sha256(str(item).encode()).hexdigest(), 16) % self.capacity
    def _alt_index(self, idx, fp):
        h = int(hashlib.sha256(fp).hexdigest(), 16)
        return (idx ^ h) % self.capacity
    def add(self, item):
        fp = self._fingerprint(item)
        i1 = self._hash(item)
        i2 = self._alt_index(i1, fp)
        for i in (i1, i2):
            if len(self.buckets[i]) < self.bucket_size:
                self.buckets[i].append(fp)
                self.count += 1
                return True
        i = random.choice([i1, i2])
        for _ in range(500):
            j = random.randrange(len(self.buckets[i]))
            fp, self.buckets[i][j] = self.buckets[i][j], fp
            i = self._alt_index(i, fp)
            if len(self.buckets[i]) < self.bucket_size:
                self.buckets[i].append(fp)
                self.count += 1
                return True
        return False
    def __contains__(self, item):
        fp = self._fingerprint(item)
        i1 = self._hash(item)
        i2 = self._alt_index(i1, fp)
        return fp in self.buckets[i1] or fp in self.buckets[i2]
    def delete(self, item):
        fp = self._fingerprint(item)
        i1 = self._hash(item)
        i2 = self._alt_index(i1, fp)
        for i in (i1, i2):
            if fp in self.buckets[i]:
                self.buckets[i].remove(fp)
                self.count -= 1
                return True
        return False

if __name__ == "__main__":
    cf = CuckooFilter()
    items = sys.argv[1:] or ["apple", "banana", "cherry"]
    for it in items: cf.add(it); print(f"Added: {it}")
    for it in items + ["missing"]: print(f"  {it!r} present: {it in cf}")
    if items: cf.delete(items[0]); print(f"Deleted: {items[0]}, present: {items[0] in cf}")
    print(f"Count: {cf.count}")
