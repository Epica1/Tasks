### Задание №5 ###

from collections import deque

class RecentCounter:
    def __init__(self):
        self.queue = deque()

    def ping(self, t):
        self.queue.append(t)
        while self.queue[0] < t - 3000:
            self.queue.popleft()
        return len(self.queue)

if __name__ == "__main__":
    recentCounter = RecentCounter()
    print(recentCounter.ping(1))
    print(recentCounter.ping(100))
    print(recentCounter.ping(3001))
    print(recentCounter.ping(3002))
