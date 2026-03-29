#!/usr/bin/env python3
"""Cuckoo filter — supports deletion unlike Bloom filters."""
import sys, hashlib, struct

class CuckooFilter:
    def __init__(self, capacity=1024, bucket_size=4, max_kicks=500):
        self.capacity = capacity
        self.bucket_size = bucket_size
        self.max_kicks = max_kicks
        self.buckets = [[] for _ in range(capacity)]
        self.count = 0
    def _fingerprint(self, item):
        h = hashlib.sha256(str(item).encode()).digest()
        return h[:2]  # 2-byte fingerprint
    def _hash(self, item):
        return int(hashlib.md5(str(item).encode()).hexdigest(), 16) % self.capacity
    def _alt_index(self, idx, fp):
        h = int(hashlib.md5(fp).hexdigest(), 16)
        return (idx ^ h) % self.capacity
    def insert(self, item):
        fp = self._fingerprint(item)
        i1 = self._hash(item)
        i2 = self._alt_index(i1, fp)
        for i in (i1, i2):
            if len(self.buckets[i]) < self.bucket_size:
                self.buckets[i].append(fp)
                self.count += 1
                return True
        import random
        i = random.choice([i1, i2])
        for _ in range(self.max_kicks):
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

def test():
    cf = CuckooFilter(64, 4)
    for i in range(20):
        assert cf.insert(f"k{i}")
    for i in range(20):
        assert f"k{i}" in cf
    assert cf.delete("k5")
    assert "k5" not in cf
    assert not cf.delete("nonexistent_xyz")
    print("  cuckoo_filter: ALL TESTS PASSED")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("Cuckoo filter — supports insert, lookup, delete")
