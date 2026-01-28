''' write a program to find the reverse of the given number'''
def reverse(n):
   rev=0
   while(n>0):
    rev=rev*10+n%10;
    n//=10
   return rev

def isPalindrome(num):
    return num==reverse(num)

print(reverse(123))
print(isPalindrome(123))
print(reverse(121))
print(isPalindrome(121))

def getPalindromes(start,end):
   res=" "
   for i in range (start ,end+1):
      if isPalindrome(i):
         res=res+str(i)+","
   return res
print(getPalindromes(1,1000))

