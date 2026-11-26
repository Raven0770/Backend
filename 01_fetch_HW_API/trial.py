
# def greet():
#     print("Execute Original Function and Stored the value, in respective variable")
#     return "hello"

# hi = greet()

# print(hi)


#! ================================================================== #

# def greet():
#     print("Hello")

# def execute_function(func):
#     func()

# execute_function(greet)

#! ================================================================== #

#^ Decorators
 #* Manual Way

# def decorator_function(func):
#     def wrapper():
#         print("Starting the function")
#         func()
#         print("Function Executed Successfully!")
#     return wrapper

# def greet():
#     print("Hello, This is fun")

# greet = decorator_function(greet)

# greet()

 #* With @ decorator 
# def decorator_function(func):
#     def wrapper():
#         print("Starting the function")
#         func()
#         print("Function Executed Successfully!")
#     return wrapper

# @decorator_function
# def greet():
#     print("Hello, This is fun")

# greet()



#!=========================================================================
#^ pref_time()

import time
x = (print(i) for i in dir(time))