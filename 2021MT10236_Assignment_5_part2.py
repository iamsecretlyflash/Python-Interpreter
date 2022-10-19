#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  5 23:44:34 2022

@author: Vaibhav Seth
"""
import sys
import keyword
l_num = 0
lines = []  # initalise to empty list
tab_count = []
instructions_raw = []
instructions = []
DATA = []
open_loops = []


"""
EXIT CODES:
    0: INVALID LOOP DEFINITION
    1: INVALID INDENTATION AND SYNTAX ERRORS"
    2: INPUT SIZE ERROR
    3: VARIABLE ERROR
    4: LOGICAL ERROR 
"""
def file_parser():
    with open('/Users/anamikaseth/Desktop/test.txt') as f:
        lines = f.readlines()  # read all lines into a list of strings
    for statement in lines:  # each statement is on a separate line
        tabs = 0
        while statement[tabs] == '\t':
            tabs += 1

        tab_count.append(tabs)
        token_list = statement.split()  # split a statement into a list of tokens
        instructions_raw.append(token_list)

    # assuming that there aren't too many tabs, and tab counting takes O(1)  time
    # file_parser os O(n) where n is the number o finput lines
    # now, for a more accurate anaylsis, if we take number of input lines to be m
    # then time taken wil be <=C*m*n
    # so we can say that it is O(m*n) but because there aren't too many tabs it is safe to say that it would be O(n)


def process_instructions():
    # TO CONVERT RAW INSTRUCTIONS(Input tokens) to a list containing Instruction objects

    n = len(instructions_raw)
    i = 0  # loop variable
    # assigning 0 indentation to final line, mostly to avoid error
    tab_count.append(0)

    while(i < n):
        # working on the ith line (Starting from 0)
        tokens = instructions_raw[i]
        l = len(tokens)
        if l < 3 or l > 5:  # Onlu Inputs of sizes 3,4,5 supported
            print("LINE {} : Size of Input not supported".format(i))
            sys.exit(2)

        tabs_i = tab_count[i]  # tabs on the current line
        tabs_i1 = tab_count[i+1]  # tabs on the next line

        # if tabs have increased then there must be a while loop or error
        # if tabs have decreased then a while loop must have ended, and depending on number of loops that are open(no corrosponding branch lines)
        # and the change in indentation, we can add the necessary branch lines

        # if indentation is same, then it's just an assignmnet statement

        if tabs_i == tabs_i1:
            if l == 3:  # a = b type
                instructions.append(Instruction(
                    "ASSIGNMENT", tokens[2], "", "", tokens[0]))  # object creation

            elif l == 4:  # not or - type
                instructions.append(Instruction(
                    "ASSIGNMENT", "", tokens[2], tokens[3], tokens[0]))
            else:  # a = b + c type
                instructions.append(Instruction(
                    "ASSIGNMENT", tokens[2], tokens[3], tokens[4], tokens[0]))

        elif tabs_i < tabs_i1:  # TABS HAVE INCREASED

            # checking if the increased indentation is due to occurence of while or not
            if tabs_i1-tabs_i > 1 or tabs_i1-tabs_i == 1 and tokens[0] != "while":
                print("LINE {} : SYNTAX ERROR : INVALID INDENTATION ".format(i))
                sys.exit(1)
            else:
                # Since, we have a while loop, we will be checking the syntax of the definition
                if l != 5:  # while a > b : has five tokens; other definitons not supported
                    print("LINE {} : SYNTAX ERROR : INVALID LOOP DEFINITION ".format(i))
                    sys.exit(0)
                # if the last token is not ':' then the declaration in incorrect
                elif tokens[-1] != ":":
                    print("LINE {} : INVALID SYNATX : ':' EXPECTED ".format(i))
                    sys.exit(0)
                elif tokens[0] != "while":  # checking the spelling of while
                    print(
                        "LINE {} : INVALID SYNTAX : while loop incorrect initialise d".format(i))
                    sys.exit(0)
                else:
                    TYPE = ""
                    if tokens[2] == "<":
                        TYPE = "BLT"
                    elif tokens[2] == ">":
                        TYPE = "BLT"
                        # switching the tokens to maintain BLT
                        tokens[1], tokens[3] = tokens[3], tokens[1]
                    elif tokens[2] == "<=":
                        TYPE = "BLE"
                    elif tokens[2] == ">=":
                        TYPE = "BLE"
                        # switching the tokens to maintain BLE
                        tokens[1], tokens[3] = tokens[3], tokens[1]
                    elif tokens[2] == "==":
                        TYPE = "BE"

                    else:
                        print("LINE {} : CONDITIONAL IN INITIALISATION OF WHILE LOOP NOT SUPPORTED".format(i))
                        sys.exit(0)
                    # NOW THAT WE HAVE ALL THE TYPES AND CORRECT ORIENTATION OF THE TOKENS, WE CAN CREATE THE OBJECT
                    # assigning -1 to the target as we still do not know where the branch statement will be
                    obj = Instruction(
                        TYPE, tokens[1], tokens[2], tokens[3], -1)
                    instructions.append(obj)
                    # Now, adding the index of the while declaration to open_loops so that when the indentations decrease
                    open_loops.append(len(instructions)-1)
                    # we can change the TARGET values accorrdingly

        else:  # now handling the case of decreasing indentations
            temp = tabs_i-tabs_i1

            # if the indentations decrease by more than the number of loops without a branch statement, then there is surely an indentation error
            if temp > len(open_loops):
                print("LINE {} : SYNTAX ERROR: KINDLY CHECK THE INDENTATIONS ".format(i))
                sys.exit(1)

            # NOW, WHEN INDENTATIONS DECREASE, THE NEXT statement WILL BE EITHER OTHER LOOP, OR ASSIGNMENT STATEMENTS.
            # Here we are handling the assignment statement that is at the ith index, and we are adding branch statement corresponding to the number of loops closed(delta Indentation)

            if l == 3:  # assignment type
                instructions.append(Instruction(
                    "ASSIGNMENT", tokens[2], "", "", tokens[0]))

            elif l == 4:  # not or - type
                instructions.append(Instruction(
                    "ASSIGNMENT", "", tokens[2], tokens[3], tokens[0]))
            else:
                instructions.append(Instruction(
                    "ASSIGNMENT", tokens[2], tokens[3], tokens[4], tokens[0]))

            # now for adding branches. Number of branches closed will be = tabs_i - tabs_i1 = temp
            # hence, running the for loop temp times, to close "temp" open loops
            for j in range(temp):
                # Extracting the index of the latest open loop, and popping it from open_loops as it's gonna get closed
                loop_def_index = open_loops.pop(-1)
                # now we have the index of the while loop, so we can create an instruction object of branch type with the TARGET as "loop_def_index"
                obj = Instruction("BRANCH", None, None, None, loop_def_index)
                instructions.append(obj)
                # Now, that we have appended a branch statement, we know that in the case of a False loop
                instructions[loop_def_index].TARGET = len(instructions)
                # loop condition, the execution goes to the line after the branch line
                # INDEX of branch will simply be the length of instructions list -1, so the inddex of next line will be lenght of instructions list

        i += 1  # icnrementing i

    # COMPLEXITY ANALYSIS :
    # let n be the numebr of input lines, of which we have m loops
    # the outer while loop runs for n times, and all the internal operations (except inner for loop) are O(1) time
    # the inner for loop wil run for a max of 'm' times as there are m loop defns and we have to close all m of them and the operations inside the loop is O(1)
    # hence the time complexity is O(m+n)





class Instruction:
    # Instructions class to create instructions object
    #
    # INITIALIZATION : TYPE : Statement (assignment type stuff)/ BLE/BLT/BE
    #               : val1 and val2 : value of operand1 and operand2 (if any) otherwise stores ""
    #               : op : stores the values of operation/comparison (if any) otherwise ""
    #               : TARGET : for loop statements, stores the final of the destination points
    #                        : for assignment statements, stores the value of the variable to which the value is being assigned

    def __init__(self, TYPE, val1, op, val2, TARGET):
        self.TYPE = TYPE
        self.op = op
        self.val1 = val1
        self.val2 = val2
        self.TARGET = TARGET

    # string representation of the object
    def __str__(self):
        return " " + str(self.TYPE) + "  " + str(self.val1) + "  " + str(self.op) + "  " + str(self.val2) + "  " + str(self.TARGET)+'\n'

    # FUNCTION TO OPERATE A GIVEN STATEMENT
    def line_operate(self, DATA):
        if self.TYPE == "ASSIGNMENT":  # for statement executions we are just gonna use the operate() function from Assignment 5 a
            # creating a line list for the function
            line = [self.TARGET, "=", self.val1, self.op, self.val2]
            self.state_operate(line, DATA)  # executing the function

        else:  # part that executes the loop statements

            val_exec_1 = 0  # to store the integer/bool value of val1

            val_exec_2 = 0  # to store the integer/bool value of val2\
            # First Handling statements like True > 0    
            if self.val1=="True":
                val_exec_1 = True
                if self.data_present(True,DATA) == -1:
                    DATA.append(True)
            elif self.val1 == "False":
                val_exec_1 = False
                if self.data_present(False,DATA)==-1:
                    DATA.append(False)
            else: # normal a > b from statements
                
                if self.val1.isalnum() and not self.val1.isnumeric():  # Checking if val1 is a variable
                    # if variable then checking it it's a valid variable definiton..... takes O(1) time ( assuming that variable names are not exceptionally long)
                    self.check_var_name(self.val1, DATA)
    
                    # now, we check if the variable name is present in the DATA list
                    a = self.data_present(self.val1, DATA)
    
                    if a == -1:
                        # if not present then we throw error
                        print("VARIABLE {} NOT DEFINED".format(self.val1))
                        sys.exit(3)
                    else:
                        # if present, then we assign the value of the variable to val_exec_1 for proper execution
                        val_exec_1 = DATA[DATA[a][1]]
                else:
                    # now considering the case where val1 is an integer
                    # searching for the INTEGER VALUE of val1
                    a = self.data_present(int(self.val1), DATA)
                    val_exec_1 = int(self.val1)
                    if a == -1:  # if not present then we append it to the loop
                        DATA.append(int(self.val1))

            # NOW DOING THE SAME THING FOR val2
            if self.val2=="True":
                val_exec_2 = True
                if self.data_present(True,DATA) == -1:
                    DATA.append(True)
            elif self.val2 == "False":
                val_exec_2 = False
                if self.data_present(False,DATA)==-1:
                    DATA.append(False)
            else:
                if self.val2.isalnum() and not self.val2.isnumeric():
                    self.check_var_name(self.val2, DATA)
                    b = self.data_present(self.val2, DATA)
                    if b == -1:
                        print("LINE {} : VARIABLE {} NOT DEFINED".format(l_num,self.val2))
                        sys.exit(3)
                    else:
                        val_exec_2 = DATA[DATA[b][1]]
                else:
                    b = self.data_present(int(self.val2), DATA)
                    val_exec_2 = int(self.val2)
                    if b == -1:
    
                        DATA.append(int(self.val2))

            # NOW CARRYING OUT THE CONDITONAL OEPRATIONS
            if self.TYPE == "BLE":
                if val_exec_1 <= val_exec_2:
                    return True
                return False
            elif self.TYPE == "BLT":
                if val_exec_1 < val_exec_2:
                    return True
                return False
            elif self.TYPE == "BE":
                if val_exec_1 == val_exec_2:
                    return True
                return False
            elif self.TYPE == "BRANCH":
                return self.TARGET
    # COMPLEXITY ANALYSIS:
        # assuming the length of DATA list before the execution is n
        # for while/branch statements, the time complexity will be O(n) as we are using the data_present function four times, which is O(n) and check_var_name is O(1)
        # for assignment statemnets : state_operate() is also O(n)
        # hence line_opearate is overall O(n), where n is the size of the DATA lsit before execution


# The following section is from assignment 5 part 1

    def state_operate(self, line, DATA):

        # we know that the first two elements of the line are a variable and = sign
        # so, let's just check from the end, if a given variable or constant is present in DATA and act accordingly
        n = len(line)
        string_to_eval = ''  # This string will store the values of integer constants and variables so that we can use eval() function
        if line[0].isnumeric() == True:  # for cases like 1 = 2 + 3
            self.cavenger(DATA)
            print(
                "LINE {} : Can't assign value to an Integer constant".format(l_num))
            sys.exit(4)
        self.check_var_name(line[0], DATA)
        if line[1] != '=':
            self.scavenger(DATA)
            print(
                "INVALID SYNTAX IN LINE {}: = expected in place of {}".format(l_num, line[1]))
            sys.exit(1)
        for i in range(2, n):  # running backwards and leaving out 0 and 1, becuase we know that the elements at indices 0 and 1 will be
            # a variable and '=' sign respectively

            # handling individual data points(variable/integer constant) of the expression
            obj = line[i]
            # Because alnum does not work on special characters # Taking O(1) assuming that variables are not huge
            obj = obj.replace('_', 'X')
            # checking for variable and Integer_Constant. Booleans are dealt later
            if obj.isalnum() and obj != 'and' and obj != 'or' and obj != 'not' and obj != 'True' and obj != 'False':
                obj = line[i]  # reverting to the original state
                if obj.isnumeric():   # Handling Integer_constants
                    line[i] = int(obj)
                    # Checking if DATA contains obj
                    x = self.data_present(int(obj), DATA)
                    if x == -1:  # if DATA doesn't contains obj, then only we'll append it to DATA
                        DATA.append(int(obj))
                else:  # Handling varaibles
                    self.check_var_name(obj, DATA)
                    x = self.data_present(obj, DATA)
                    if x == -1:  # If a variable is not already present in DATA, raise Variable not defined error
                        print(
                            "LINE {} : Variable '{}' is not defined".format(l_num, obj))
                        sys.exit(4)
                    else:
                        # replacing the variable with its integer value to aid calculation. Original variable data is not lost
                        line[i] = DATA[DATA[x][1]]

            elif obj == 'True':  # handling boolean values
                # converting string to actual boolean values for calculations
                line[i] = True
                # Append True, only if it's not present
                if self.data_present(True, DATA) == -1:
                    DATA.append(line[i])

            elif obj == 'False':  # handing False
                # converting string to actual boolean values for calculations
                line[i] = False
                # Append False, only if it's not present
                if self.data_present(line[i], DATA) == -1:
                    DATA.append(line[i])

            # dealing with -1 or -a type of LINEs
            elif len(obj) == 2 and (obj[1].isalnum() and obj[0] == '-'):
                obj = line[i]
                if obj[1].isnumeric():   # Handling Integer_constants
                    line[i] = int(obj)
                    # Checking if DATA contains obj
                    x = self.data_present(int(obj), DATA)
                    if x == -1:  # if DATA doesn't contains obj, then only we'll append it to DATA
                        DATA.append(int(obj))
                else:  # Handling varaibles
                    self.check_var_name(obj[1], DATA)
                    x = self.data_present(obj, DATA)
                    if x == -1:  # If a variable is not already present in DATA, raise Variable not defined error
                        print(
                            "LINE {}: Variable '{}' is not defined".format(l_num, obj[1]))
                        sys.exit(4)
            # concatenating the value of the integer constant/operator to the string to be evaluates using eval
            string_to_eval = string_to_eval + str(line[i]) + " "

        # calculatign the answer using eval function
        ans = eval(string_to_eval)
        # if the calculated answer is not present, then we append it to DATA
        if self.data_present(ans, DATA) == -1:
            DATA.append(ans)

        # assigning ans to the leftmost variable
        self.assign(line[0], ans, DATA)

        # COMPLEXITY ANALYSIS :
        # let lenght of DATA before execution be n
        # during execution the DATA list can increase by at most 2
        #
        # now, assuming that no errors, occur and scavenger() isn't called.
        #
        # throughout the if else statements, we will be calling data_present for a maximum of two times
        # since, the input size isn't too large we can take eval(), check_var_name() and other stricg functions as O(1)
        #
        # assign takes O(n) time, as it calls data_present() which takes O(n) time
        #
        # hence total time taken will be 2*k*n + c*(n+2) + d*(n+2);  k,c,d are constants independent of n
        # Hence, we can take the time complexity of the funtion to be to be O(n)

        #
        # If anywhere the scavenger function is encountered the the time complexity increases to O(n^2)

    def check_var_name(self, var, DATA):
        # INPUT : a variable
        # Checks if a vraible name is correct according to the python convention
        # THIS FUNCTION IS O(1) IF THE VARIABLE NAME IS CORRECT as it just involves condition checking
        # IF THE VARIABLE NAME IS INCORRECT, WE EXECUTE THE SCANVENGER FUNCTION WHICH IS  O(n^2)
        if len(var) == 1 and var.isalpha() == False:
            self.scavenger(DATA)
            print(
                "INVALID SYNTAX IN LINE {}: '{}' INVALID VARIABLE NAME".format(l_num, var))
            sys.exit(3)
        if var[0].isdigit():
            # Name can't start with a digit
            self.scavenger(DATA)
            print(
                "LINE {}: VARIABLE NAME CANNOT START WITH A DIGIT".format(l_num))
            sys.exit(3)
        if keyword.iskeyword(var):  # Variable  canmnot be a keword
            self.scavenger(DATA)
            print(
                "LINE {}: VARIABLE NAME CANNOT BE A KEYWORD".format(l_num))
            sys.exit(3)
        for char in var:
            if not(char.isalnum() or char == '_'):  # Varibale can't have symbols other than _
                self.scavenger(DATA)
                print(
                    "LINE {}: VARIABLE NAME CANNOT CONTAIN ANY SPECIAL CHARACTERS OTHER THAN '_'".format(l_num))
                sys.exit(3)

    def data_present(self, a, DATA):  # Checks if a data point or a variable is present in DATA
        # LINE: element to be checked(can be a variable or integer)
        # OUTPUT: index of the element in DATA list if present otherwise -1

        loc = 0

        # INVARIANT: for all elements before i ; a is not equal to that element(integer or variable)
        #          : loc stores the index of i elements
        for i in DATA:
            # Check for variable. Since variable is stored as a tuple type(i) has to be a tuple
            if type(a) == str and type(i) == tuple and a == i[0]:
                return loc

            # Check for integer or booleans. type of both of have to be int or bool
            elif type(a) == type(i) and a == i:
                return loc
            loc += 1  # increase loc by 1
        return -1  # if a is not present
        # let n = len(DATA)
        # Time Complexity = O(n)

    def assign(self, var, val, DATA):
        # Used to assign the reference of the value a variable is referring to
        # If the variable is not pre-existing, creates a new tuple for the variable
        # If the variable exists, replaces the tuple with a new one that contains the new reference value

        # stores the location of the value (has to exist)
        val_pos = self.data_present(val, DATA)
        # stores the location of the variable (>=0 if pre-existing, -1 if does not exist)
        var_pos = self.data_present(var, DATA)

        if var_pos == -1:  # if variable does not exist in DATA, we create a new data point for that Variable in DATA list
            DATA.append((var, val_pos))
        else:  # replacing the pre-existing tuple with a new one
            DATA[var_pos] = (var, val_pos)

        # let n be the length of DATA of before any changes
        # Time Complexity : O(2n) which is basically O(n)
        #  becuase the function basically calls data_present twice which has TC O(n),
        #  and does some O(1) condition checking and O(1) assignment/append

    # A cool name XD for my garbage collection method and a method to display values of the variables
    def scavenger(self, DATA):

        # no LINEs arguments. function operates on the global DATA list
        # OUPUT : 1) Variables which have an assigned value
        #       : 2) Garbage values as a list

        # O(n^2), where n is the size of the DATA list, becuase we have basically two loops running n times

        res = []  # List to to store Garbage values

        # INVARIANT : each element ele in DATA that comes before i element:
        #             if ele is not assigned to any variable, ele is present in res

        for i in DATA:  # terminates when all elements are checked

            if type(i) != tuple:  # Since, integer objects are the garbage we are looking for

                used = False
                for j in DATA:  # to check if i is garbage or not; if not the used = True, and print all the variables associated with i
                    if type(j) == tuple and type(DATA[j[1]]) == type(i) and DATA[j[1]] == i:
                        print("{} = {}".format(j[0], DATA[j[1]]))
                        used = True
                if used == False:  # if i is not used then append to res
                    res.append(i)
        print("Garbage Values : {}".format(res))  # Printing garbage values
        
def operate():
    global l_num
    n = len(instructions)
    LOOP_VAR = 0
    while(LOOP_VAR < n):
        l_num = LOOP_VAR
        curr = instructions[LOOP_VAR]
        if curr.TYPE == "BRANCH":
            LOOP_VAR = curr.TARGET
            (curr.scavenger(DATA))
        elif curr.TYPE == "BLE" or curr.TYPE == "BLT" or curr.TYPE == "BE":
            A = curr.line_operate(DATA)
            if A == True:
                LOOP_VAR += 1
            else:
                LOOP_VAR = curr.TARGET
        else:
            curr.line_operate(DATA)
            LOOP_VAR += 1

    (curr.scavenger(DATA))

    # time complexity will depend on the number of inputs to DATA list, and the number of loops, and loop conditoin
    # I have attached two test cases to show the same

def main():
    file_parser()
    process_instructions()
    print("Instructions List : ")
    for i in range(len(instructions)):
        print("{}. {}".format(i,instructions[i]))
    print()
    operate()
    # NET TIME COMPLEXITY :
    # n input lines, with m while loops
    # Time for instructions_final is O(m+n)
    # then there is another O(m+n) loop for printing instruction objects
    # 


def check():
    n = len(DATA)
    for i in range(n):
        for j in range(n):
            if i != j:
                if type(DATA[i]) == type(DATA[j]) == tuple:
                    if DATA[i]==DATA[j]:
                        print(i)
                elif type(DATA[i])==type(DATA[j]) and DATA[i]==DATA[j]:
                    if i== j:
                        print(i)
    print("TEST PASSED")
if __name__ == "__main__":
    main()

"""
TEST CASE 1:

a = 10 
while a > 0 :   
    a = a -1
b = a + 100

INSTRUCTION CODE :
START
0. a = 10
1. BLT 0,a 4
2. a = a -1
3. BRANCH 1
4. b = a + 100
STOP

OUTPUT : 
    TYPE        val1  op  val2    TARGET
    ASSIGNMENT  10                   a
    
    BLT         0     >    a         4

    ASSIGNMENT  a     -    1         a

    BRANCH     None  None  None      1

    ASSIGNMENT  a     +    100       b


a = 9
Garbage Values : [10, 0, -1]
a = 8
Garbage Values : [10, 0, -1, 9]
a = 7
Garbage Values : [10, 0, -1, 9, 8]
a = 6
Garbage Values : [10, 0, -1, 9, 8, 7]
a = 5
Garbage Values : [10, 0, -1, 9, 8, 7, 6]
a = 4
Garbage Values : [10, 0, -1, 9, 8, 7, 6, 5]
a = 3
Garbage Values : [10, 0, -1, 9, 8, 7, 6, 5, 4]
a = 2
Garbage Values : [10, 0, -1, 9, 8, 7, 6, 5, 4, 3]
a = 1
Garbage Values : [10, 0, -1, 9, 8, 7, 6, 5, 4, 3, 2]
a = 0
Garbage Values : [10, -1, 9, 8, 7, 6, 5, 4, 3, 2, 1]
a = 0
b = 100
Garbage Values : [10, -1, 9, 8, 7, 6, 5, 4, 3, 2, 1]

DATA : [10, ('a', 2), 0, -1, 9, 8, 7, 6, 5, 4, 3, 2, 1, 100, ('b', 13)]

    
TIME COMPLEXITY : 
    let the number of lines be n = 4
    number of while loops, m = 1
    number of instruction statements = m+n
    I will be ignoring the time complexity of file_parser for now
    time complexity of instructions_final is O(m+n), let's say it takes C*(m+n) time
    for time complexity of operate :
        let the number of maximum data elements being added to DATA be MAX_ELE
        Now, since we deduced that each line execution inside operate will be O(MAX_ELE)
        Therefore, we can say that for m+n instructions, the time taken will be <= (m+n)*MAX_ELE* C2..... where C2 is some constant
        Hence the total time complexity will be <= C3*(m+n)*MAX_ELE or O(n*MAX_ELE)\
     In the given example the final DATA list is : [10, ('a', 2), 0, 1, 9, 8, 7, 6, 5, 4, 3, 2, 100, ('b', 12)], which as 14 elements ( the numbers in middle come from decrement of a in loop)
     so, we can say that the execution takes some C3*14*5 units of time

TEST CASE 2 :

a = 10
b = 0
while a > b :
	b = 5
	a = a - 1
	while b < 10 :
		b = b + 1
	a = a + 1
b = 100

OUPUT : 
Instructions list : 
    TYPE        val1  op  val2    TARGET
 ASSIGNMENT     10                  a

 ASSIGNMENT      0                  b

     BLT        b     >    a        10

 ASSIGNMENT     5                    b

 ASSIGNMENT     a     -     1        a

 BLT            b     <     10       8

 ASSIGNMENT     b     +     1        b

 BRANCH        None  None  None      5

 ASSIGNMENT     a     +     1        a

 BRANCH       None   None  None      2

 ASSIGNMENT    100                   b


    a = 9
    b = 6
    Garbage Values : [10, 0, 5, 1]
    a = 9
    b = 7
    Garbage Values : [10, 0, 5, 1, 6]
    a = 9
    b = 8
    Garbage Values : [10, 0, 5, 1, 6, 7]
    a = 9
    b = 9
    Garbage Values : [10, 0, 5, 1, 6, 7, 8]
    b = 10
    a = 9
    Garbage Values : [0, 5, 1, 6, 7, 8]
    a = 10
    b = 10
    Garbage Values : [0, 5, 1, 9, 6, 7, 8]
    a = 10
    b = 100
    Garbage Values : [0, 5, 1, 9, 6, 7, 8]


 
 DATA : [10, ('a', 0), 0, ('b', 10), 5, 1, 9, 6, 7, 8, 100]

TIME COMPLEXITY: 
    Here we have total of 9 line and 2 loops. The length of DATA is 11
    Hence, the time compelxity will be <= C3*11*11 units of time
    

"""
