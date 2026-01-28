''' write a program to find the reverse of the given number'''
n=int (input('enter a number:'))
rev=0
while(n>0):
    rev=rev*10+n%10;
    n//=10
print ("rev number is:",rev)
