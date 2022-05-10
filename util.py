import heapq
import math

class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """
    def  __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)

def euclideanDist(pos1,pos2):
    return math.sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)

def manhattanDist(pos1,pos2):
    return (abs(pos1[0]-pos2[0]) + abs(pos1[1]-pos2[1]))

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y
    
    def getValue(self):
        return [self.x,self.y]



class ListPaths:
    def __init__(self,path):
        self.path=path
    
    def getValue(self):
        return self.path

    
def adapt_Listpath(listPath):
    return (';'.join(["%d;%d" % a for a in listPath.path])).encode('ascii')

def adapt_point(point):
    return ("%d;%d" % (point.x, point.y)).encode('ascii')

def convert_ListPath(listPath):
    split = listPath.split(b";")
    l = len(split)
    npath = [[int(split[i+1]),int(split[i])] for i in range(0,l,2)]
    return ListPaths(npath)

def convert_point(s):
    l =  s.split(b";")
    return Point(int(l[0]),int(l[1]))

