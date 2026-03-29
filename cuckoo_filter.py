#!/usr/bin/env python3
"""cuckoo_filter - Cuckoo filter for approximate set membership with deletion."""
import sys, json, hashlib, random

class CuckooFilter:
    def __init__(self, capacity=1024, bucket_size=4, fp_size=8, max_kicks=500):
        self.capacity = capacity; self.bucket_size = bucket_size
        self.fp_size = fp_size; self.max_kicks = max_kicks
        self.buckets = [[None]*bucket_size for _ in range(capacity)]
        self.count = 0
    
    def _fingerprint(self, item):
        h = int(hashlib.sha256(str(item).encode()).hexdigest(), 16)
        fp = h % (1 << self.fp_size)
        return fp if fp else 1
    
    def _hash1(self, item):
        return int(hashlib.md5(str(item).encode()).hexdigest(), 16) % self.capacity
    
    def _hash2(self, i1, fp):
        return (i1 ^ int(hashlib.md5(str(fp).encode()).hexdigest(), 16)) % self.capacity
    
    def insert(self, item):
        fp = self._fingerprint(item)
        i1 = self._hash1(item); i2 = self._hash2(i1, fp)
        for i in [i1, i2]:
            for j in range(self.bucket_size):
                if self.buckets[i][j] is None:
                    self.buckets[i][j] = fp; self.count += 1; return True
        i = random.choice([i1, i2])
        for _ in range(self.max_kicks):
            j = random.randint(0, self.bucket_size - 1)
            fp, self.buckets[i][j] = self.buckets[i][j], fp
            i = self._hash2(i, fp)
            for j in range(self.bucket_size):
                if self.buckets[i][j] is None:
                    self.buckets[i][j] = fp; self.count += 1; return True
        return False
    
    def lookup(self, item):
        fp = self._fingerprint(item)
        i1 = self._hash1(item); i2 = self._hash2(i1, fp)
        return fp in self.buckets[i1] or fp in self.buckets[i2]
    
    def delete(self, item):
        fp = self._fingerprint(item)
        i1 = self._hash1(item); i2 = self._hash2(i1, fp)
        for i in [i1, i2]:
            for j in range(self.bucket_size):
                if self.buckets[i][j] == fp:
                    self.buckets[i][j] = None; self.count -= 1; return True
        return False
    
    def load_factor(self):
        total = self.capacity * self.bucket_size
        return self.count / total

def main():
    cf = CuckooFilter(capacity=256, bucket_size=4)
    print("Cuckoo filter demo\n")
    for i in range(200): cf.insert(f"item_{i}")
    tp = sum(1 for i in range(200) if cf.lookup(f"item_{i}"))
    fp = sum(1 for i in range(200, 400) if cf.lookup(f"item_{i}"))
    print(f"  Inserted 200, true positives: {tp}/200")
    print(f"  False positives (200 tests): {fp} ({fp/200*100:.1f}%)")
    print(f"  Load factor: {cf.load_factor()*100:.1f}%")
    for i in range(0, 200, 2): cf.delete(f"item_{i}")
    post_del = sum(1 for i in range(0, 200, 2) if cf.lookup(f"item_{i}"))
    print(f"  After deleting 100: false lookups={post_del}")

if __name__ == "__main__":
    main()
