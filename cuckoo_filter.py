#!/usr/bin/env python3
"""cuckoo_filter - Cuckoo filter for set membership."""
import argparse, hashlib, random, sys

class CuckooFilter:
    def __init__(self, capacity=1024, bucket_size=4, fp_size=8, max_kicks=500):
        self.cap = capacity; self.bs = bucket_size; self.fps = fp_size
        self.max_kicks = max_kicks; self.count = 0
        self.buckets = [[None]*bucket_size for _ in range(capacity)]
    def _fingerprint(self, item):
        h = hashlib.sha256(str(item).encode()).digest()
        return int.from_bytes(h[:self.fps//8+1], "big") % (2**self.fps - 1) + 1
    def _hash(self, item):
        return int(hashlib.md5(str(item).encode()).hexdigest(), 16) % self.cap
    def _alt_index(self, idx, fp):
        return (idx ^ int(hashlib.md5(str(fp).encode()).hexdigest(), 16)) % self.cap
    def insert(self, item):
        fp = self._fingerprint(item); i1 = self._hash(item); i2 = self._alt_index(i1, fp)
        for idx in (i1, i2):
            for j in range(self.bs):
                if self.buckets[idx][j] is None:
                    self.buckets[idx][j] = fp; self.count += 1; return True
        idx = random.choice([i1, i2])
        for _ in range(self.max_kicks):
            j = random.randrange(self.bs)
            fp, self.buckets[idx][j] = self.buckets[idx][j], fp
            idx = self._alt_index(idx, fp)
            for j in range(self.bs):
                if self.buckets[idx][j] is None:
                    self.buckets[idx][j] = fp; self.count += 1; return True
        return False
    def contains(self, item):
        fp = self._fingerprint(item); i1 = self._hash(item); i2 = self._alt_index(i1, fp)
        return fp in self.buckets[i1] or fp in self.buckets[i2]
    def delete(self, item):
        fp = self._fingerprint(item); i1 = self._hash(item); i2 = self._alt_index(i1, fp)
        for idx in (i1, i2):
            if fp in self.buckets[idx]:
                self.buckets[idx][self.buckets[idx].index(fp)] = None
                self.count -= 1; return True
        return False

def main():
    p = argparse.ArgumentParser(description="Cuckoo filter")
    p.add_argument("--demo", action="store_true", default=True)
    a = p.parse_args()
    cf = CuckooFilter(1024)
    for i in range(500): cf.insert(f"item_{i}")
    fp = sum(1 for i in range(10000) if cf.contains(f"fake_{i}"))
    print(f"Inserted 500 items, tested 10000 non-members")
    print(f"False positives: {fp} ({100*fp/10000:.2f}%)")
    print(f"Size: {cf.count}")
    cf.delete("item_0")
    print(f"After delete item_0: contains={cf.contains('item_0')}")
    print(f"item_1 still there: {cf.contains('item_1')}")

if __name__ == "__main__": main()
