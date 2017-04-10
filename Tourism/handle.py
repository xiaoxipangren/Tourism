import re
src=open('userpois.csv','rt',encoding='utf-8')
dest=open('handledsuserpois.csv','rt',encoding='utf-8')

lines=src.readlines()
length=len(lines)
line=None
index=0
while index<length:
    line=lines[index]
    if(line=='\n'):
        index=index+1
        continue

    if(len(line.split(','))<17):
        i=index+1
        s=lines[i]
        while i<length and len(s.split(','))<17 and not s.split(',')[0].isdigit():
            if(s!='\n'):
                line=line+s
            i=i+1
            s=lines[i]
        line=line.replace('\n',' ')+'\n'
        index=i-1
    index=index+1
    dest.write(line)

