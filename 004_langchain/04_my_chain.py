class TestChain:
    def __init__(self, name):
        self.name = name

    def __or__(self, other):
        runner = ChainRunner(self, other)
        return runner
    
    def run(self, name):
        print(f"我是{self.name},我的执行了是{name}")
        return self.name

class ChainRunner:
    def __init__(self, *args):
        self.queue = []
        for a in args:
            self.queue.append(a)
        
    def __or__(self, other):
        self.queue.append(other)
        return self
    
    def run(self, *args):
        ans = args[0] if len(args) == 1 else args
        for runable in self.queue:
            ans = runable.run(ans)
        return ans


a = TestChain("A")
b = TestChain("B")
c = TestChain("C")

chain = a | b | c
res = chain.run("小蓝")

print(res)