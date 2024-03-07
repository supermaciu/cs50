class Stack:
    s = []

    def push(self, element):
        self.s.append(element)

    def pop(self):
        return self.s.pop()

    def top(self):
        return self.s[-1]

stack = Stack()

stack.push(2)
stack.push(3)

print(stack.top())

stack.push(4)

print(stack.top())

stack.pop()

print(stack.top())