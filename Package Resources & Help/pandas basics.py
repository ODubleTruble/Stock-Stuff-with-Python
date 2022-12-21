import pandas as pd

print('-----------------------START-----------------------')

print('\nBasic Series:')
# Create a series, which is a 1D array like a column, that contains float values.
new_s = pd.Series(dtype='float64')
print(f'new_s: {new_s}')


print('\nlist to series:')
# Converting a list to a Series.
a_list = [12, 16, 7, 19, 2]
l_to_s = pd.Series(a_list)
print(f'l_to_s:\n{l_to_s}')


print('\nseries with custom index:')
# Create a series with a custom index. 
custom_index_s = pd.Series(a_list, index=['twelve', 'sixteen', 'seven', 'nineteen', 'two'])
print(custom_index_s)


print('\ndictionary to series')
# Turns a dictionary into a series.
a_dict = {
    'one' : 1,
    'two' : 2,
    'three' : 3
}
dict_to_s = pd.Series(a_dict)
print(dict_to_s)


print('\nempty data frame:')
# Creates an empty data frame.
df1 = pd.DataFrame()
print(df1)


print('\ncreate a dataframe using a list:')
# Creates a dataframe using a list.
some_list = ['test1', 'test2', 'test3']
df2 = pd.DataFrame(some_list)
print(df2)


print('\ncreate a dataframe using a list of lists:')
# Create a dataframe using a list of lists.
some_data = [['Alex', 601], ['Bob', 602], ['Cataline', 603]]
df3 = pd.DataFrame(some_data, columns = ['Name', 'Roll No.'])
print(df3)


print('\nUse zip() to merge lists:')
# Use zip() to merge lists.
list1 = ['Alex', 'Bob', 'Cataline']
list2 = [601, 602, 603]
zippedList = list(zip(list1, list2))
print(zippedList)
df4 = pd.DataFrame(zippedList, columns=['Name', 'Roll No.'])
print(df4)


print('\nRead a csv file:')
# Read an online csv file.
df5 = pd.read_csv('https://raw.githubusercontent.com/Yuvrajchandra/Basic-Operations-Using-Pandas/main/biostats.csv')
print(df5)


print('\nUse .head and .tail:')
# Use .head() to get the first few items and .tail() to get the last few
# Putting an integer in the parameters specifies the number to get from that end (default 5)
print(df5.head())
print(df5.tail(2))


print('\nDisplay info on a dataframe:')
# Displays info on a df
print(df5.info())


print('\nGet specific information from cells in a dataframe.')
# Get specific information from cells in a dataframe.
print(df5.iloc[0])
print(df5.iloc[0]['Name'])
