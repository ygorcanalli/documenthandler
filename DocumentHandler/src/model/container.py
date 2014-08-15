"""
Created on Apr 30, 2014

@author: ygor
"""
from collections import Counter


class List(list):
    def to_bag(self):
        result = Bag()
        result.update(self)
        return result
    
    def to_set(self):
        return Set(self)
    
    def to_list(self):
        return self

    def to_hash_list(self):
        hash_list = List()
        for listi in self:
            hash_list.append(listi.__hash__())
        return hash_list
    
    def __str__(self):
        return "List(" + super(List, self).__str__() + ")"
    

class Bag(Counter):
    def to_bag(self):
        return self
    
    def to_list(self):
        return List(self.elements())
      
    def to_set(self):
        return Set(self)
    

class Set(set):
    def to_bag(self):
        result = Bag()
        result.update(self)
        return result
    
    def to_set(self):
        return self
    
    def to_list(self):
        return List(self)

    def to_hash_list(self):
        hash_list = List()
        for listi in self:
            hash_list.append(listi.__hash__())
        return hash_list
