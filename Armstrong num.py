n=int(input("enter a number"))
temp=n
s=0
while n>0:
    r=n%10
    s=s+(r*r*r)
    s=s+(r**3)
    n=n//10
    print(s)
if temp == s:
    print("Armstrong number")
else:
    print("Not Armstrong number")
