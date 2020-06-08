import re
import string
import time
import operator
import sys
start_time = time.time()

#variables and txt files

arg = sys.argv[1]
arg2 = ""

l = len(sys.argv)
if(l == 3):
    arg2 = sys.argv[2]

res = []

corpus = "corpus.txt"
file = open(corpus, "rt")
corpus = file.read()
file.close

spellErrors = "spell-errors.txt"
file = open(spellErrors, "rt")
spellErrors = file.read()
spellErrors = spellErrors.replace(":", ",")
spellErrors = spellErrors.split("\n")
file.close


testCorrect = "test-words-correct.txt"
file = open(testCorrect, "rt")
testCorrect = file.read().split()
file.close

testFalse = arg
file = open(testFalse, "rt")
testFalse = file.read().split()
file.close

# corpus words
words = corpus.split(r"[a-zA-Z]+")[0].split()
table = str.maketrans("", "", string.punctuation)
newcorpus = [w.translate(table).lower() for w in words if(len(w) > 4)]
corpus = list(set(newcorpus))

#print(len(testFalse))


#lis = ['commencement, commencment, commencemend', 'suppressing, supressing', 'tonner, toner', 'sash, sach']

# print(words[:200])

#confusion matrix initilazation
delconf = [[0 for i in range(27)] for i in range(27)]
repconf = [[0 for i in range(27)] for i in range(27)]
transconf = [[0 for i in range(27)] for i in range(27)]
insconf = [[0 for i in range(27)] for i in range(27)]


def edits1(words):
    "All edits that are one edit away from `word`."
    letters = "abcdefghijklmnopqrstuvwxyz"
    deletes = []
    transposes = []
    replaces = []
    inserts = []
    word = words[0]
    wrongs = words[1:]
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    #print(wrongs)
    for L, R in splits:
        if R:
            deletes.append(L + R[1:])
            if deletes[-1] in wrongs and L and 124 > ord(R[0]) > 96 and 124 > ord(L[-1]) > 96:
                delconf[ord(L[-1])-97][ord(R[0])-97] += 1
                #print("del ")
        if len(R) > 1:
            transposes.append(L + R[1] + R[0] + R[2:])
            if transposes[-1] in wrongs and 124 > ord(R[0]) > 96 and 124 > ord(R[1]) > 96:
                transconf[ord(R[0])-97][ord(R[1])-97] += 1
                #print("tra ")
        for c in letters:
            if R:
                replaces.append(L + c + R[1:])
                if replaces[-1] in wrongs and 124 > ord(R[0]) > 96 :
                    repconf[ord(c)-97][ord(R[0])-97] += 1 
                    #print("rep ")
        for c in letters:
            inserts.append(L + c + R )
            if inserts[-1] in wrongs and L and  123 > ord(L[-1]) > 96:
                insconf[ord(L[-1])-97][ord(c)-97] += 1 
                
    return set(deletes + transposes + replaces + inserts)

#creating confusion matrices
for ind in range(len(spellErrors)):
    lis = [i.strip() for i in spellErrors[ind].split(',')]
    edits1(lis)



#prin1t(lis)

#print(delconf)


#check for edit distance one or not and return what operation needed with letters
def isEditDistanceOne(s1, s2):   
    #  lengths of  strings 
    m = len(s1) 
    n = len(s2) 
  
    
    #strings can't be at one distance 
    if abs(m - n) > 1: 
        return False 
  
    count = 0    # Count of isEditDistanceOne 
    operation = ""
    #print(s1,s2)
    i = 0
    j = 0
    while i < m and j < n: 
        # If current characters dont match
        if(count > 1 ):
            return False
        if s1[i] != s2[j]:
            if(i < m-1 and j < n-1):
                
                if count == 0 and s1[i+1] == s2[j] and s1[i] == s2[j+1]: 
                    operation = ["trans",s2[j],s1[i]]
                    i+=1
                    j+=1
                    count+=1
                elif(s1[i-1] == s2[j] and s1[i] == s2[j-1]): 
                    i+=1
                    j+=1
                elif(count > 0 ):
                    return False
                elif m > n:
                    if(s1[i+1:] == s2[j:]):
                        operation = ["ins ", s1[i] , s1[i-1] ] 
                    i+=1
                    count+=1
                elif m < n:
                    if(s1[i:] == s2[j+1:]):
                        operation = ["del ", s2[j] , s2[j+1] ] 
                    j+=1
                    count+=1
                else:    # If lengths of both strings is same
                    if(s1[i+1:] == s2[j+1:]):
                        operation = ["sub", s1[i],s2[j]] 
                    i+=1
                    j+=1
                    count+=1
                    #print("repl ",s1[i],s2[j])

            #  to remove a character
            elif(s1[i-1] == s2[j] and s1[i] == s2[j-1]): 
                i+=1
                j+=1
            elif m > n:
                operation = ["ins ", s1[i] , s1[i-1] ] 
                i+=1
                count+=1
            elif m < n and j+1<n:
                operation = ["del ", s2[j] , s2[j+1] ] 
                j+=1
                count+=1
            else:    # both strings is same
                operation = ["sub", s1[i],s2[j]] 
                i+=1
                j+=1
                count+=1 
        
                
  
            # Increment count of edits 
            
  
        else:    # if current characters match 
            i+=1
            j+=1
  
    # if last character is extra in any string
    
    if i < m or j < n and count == 0:
        if(n>m):
            operation = ["del ", s2[j-1] , s2[j] ]
        elif(m>n) and i>1:
            operation = ["ins", s1[i-1],s1[i]]

        count+=1
    if(count==1):
        return operation
    else:
        return False



def probW(s):
    return newcorpus.count(s) / len(newcorpus)

#language model p(w) *  p(x|w)
def calcProb(str1,str2,operation):
    operation[1] = ord(operation[1])-97
    operation[2] = ord(operation[2])-97
    if operation[0] == "del":
        tot = sum(row[operation[2]] for row in delconf)
        pxw = (delconf[operation[1]][operation[2]]) / tot
        pw = probW(str2)
        return pxw * pw
    elif operation[0] == "ins":
        tot = sum(row[operation[2]] for row in insconf)
        pxw = (insconf[operation[1]][operation[2]]) / tot
        pw = probW(str2)
        return pxw * pw
    elif operation[0] == "trans":
        tot = sum(row[operation[2]] for row in transconf)
        pxw = (transconf[operation[1]][operation[2]]) / tot
        pw = probW(str2)
        return pxw * pw
    elif operation[0] == "sub":
        tot = sum(row[operation[2]] for row in repconf)
        pxw = (repconf[operation[1]][operation[2]]) / tot
        pw = probW(str2)
        return pxw * pw
    return 0

# noisy language model p(w) *  p(x|w) with adding alpha=1
def noisy_calcProb(str1,str2,operation):
    operation[1] = ord(operation[1])-97
    operation[2] = ord(operation[2])-97
    if operation[0] == "del":
        tot = sum(row[operation[2]] for row in delconf)
        pxw = (delconf[operation[1]][operation[2]]+1) / (tot + 27)
        pw = probW(str2)
        return pxw * pw
    elif operation[0] == "ins":
        tot = sum(row[operation[2]] for row in insconf)
        pxw = (insconf[operation[1]][operation[2]]+1) / (tot + 27)
        pw = probW(str2)
        return pxw * pw
    elif operation[0] == "trans":
        tot = sum(row[operation[2]] for row in transconf)
        pxw = (transconf[operation[1]][operation[2]]+1) / (tot + 27)
        pw = probW(str2)
        return pxw * pw
    elif operation[0] == "sub":
        tot = sum(row[operation[2]] for row in repconf)
        pxw = (repconf[operation[1]][operation[2]]+1) / (tot + 27)
        pw = probW(str2)
        return pxw * pw
    return 0


def corrector():
    testprob = {}
    for i in testFalse:
        for j in corpus:
            a = isEditDistanceOne(i,j)
            if(a):
                testprob[j] = calcProb(i,j,a)
        asc = dict(sorted(testprob.items(), key=operator.itemgetter(1),reverse=True))
        if asc:
            res.append(list(asc)[0])
        else:
            res.append("")
        testprob = {}
        #print(testprob)
    #print(len(onedistance))





def noisy_corrector():
    testprob = {}
    for i in testFalse:
        for j in corpus:
            a = isEditDistanceOne(i,j)
            if(a):
                testprob[j] = noisy_calcProb(i,j,a)
        asc = dict(sorted(testprob.items(), key=operator.itemgetter(1),reverse=True))
        if asc:
            res.append(list(asc)[0])
        else:
            res.append("")
        testprob = {}


def writeConfMatrix():
    print('\n'.join([''.join(['{:4}'.format(item) for item in row]) 
        for row in repconf]))


if arg2:
    noisy_corrector()
else:
    corrector()


def writeFile():
    f = open("corrects.txt" , "w")
    for i in range(len(res)):
        f.write(res[i] + "\n")
    f.close()

writeFile()

def diffcount():
    ct = 0
    for i in range(len(res)):
        if(res[i] == testCorrect[i]):
            ct += 1
    print("coorect words count: ",ct)
    return 100 * ct / len(res)

print("accuracy score(percentage): ", diffcount())


#print("--- %s seconds ---" % (time.time() - start_time))

