count_id = 100
a = str(000)+str(000)+str(000)
b = str(000)+str(000)
c = str(000)
if count_id <= 9 :
  count = a+str(count_id)
elif count_id >= 10 and count_id <= 99   :
  count = b+str(count_id)
else :
  count = c+str(count_id)
  
print(count)  