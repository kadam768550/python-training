s1 = float(input("Enter marks for Subject 1: "))

s2 = float(input("Enter marks for Subject 2: "))

s3 = float(input("Enter marks for Subject 3: "))

s4 = float(input("Enter marks for Subject 4: "))

s5 = float(input("Enter marks for Subject 5: "))





total = s1 + s2 + s3 + s4 + s5

percentage = total / 5





print("Total Marks:", total)

print("Percentage:", percentage)





if percentage >= 75:

    print("Result: Distinction")

elif percentage >= 60:

    print("Result: First Class")

elif percentage >= 45:

    print("Result: Pass")

else:

    print("Result: Fail")