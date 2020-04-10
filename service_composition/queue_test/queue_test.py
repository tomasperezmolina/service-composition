from persistqueue import Queue
from threading import Thread
import time
import shutil

path = "./queue_data" #this should be a temp directory, so the file is deleted later
q = Queue(path)

def task1():
    for i in range(0, 100, 10):
        [q.put(j, timeout=1) for j in range(i, i + 10)]
        print("Task1 put 10 items: {}-{}", i, i+10)
        time.sleep(0.2)

def task2():
    count = 0
    while count < 100:
        if(not q.qsize() >= 10):
            print("Task2 sleeping for .5 seconds")
            time.sleep(.5)
        else:
            items = [q.get() for _ in range(0, 10)]

            #calling task_done() for every item we get()
            [q.task_done() for _ in range(0, 10)]

            count += 10
            print("Task2 popped items: {}", items)

t1 = Thread(target=task1)
t1.start()
t2 = Thread(target=task2)
t2.start()
t1.join()
t2.join()

print("done")

q.join()

del q
#Delete file manually since we are not using a temp path
shutil.rmtree(path)


'''
q.put('a')
q.put('b')
q.put('c')
print(q.get())
q.task_done()
print(q.get())
q.task_done()
print(q.get())
q.task_done()
'''
