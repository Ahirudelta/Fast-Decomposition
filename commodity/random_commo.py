import random
def random_commo(num_nodes, num_commo):
    commo_set = []
    for _ in range(num_commo):
        i = random.choice([k for k in range(num_nodes)])
        j = random.choice([k for k in range(num_nodes)])
        while i == j or (i,j) in commo_set:
            j = random.choice([k for k in range(num_nodes)])
        commo_set.append((i,j))
    return(commo_set)



numnodes = [16,32,64,128]
for n in numnodes:
    num_commo = int(n*(20/100))
    print("numnodes =",n)
    for _ in range(1000):
        randomm = random_commo(n,num_commo)
        print(randomm)
