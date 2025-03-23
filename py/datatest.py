import math

with open('tuple_file.txt', 'r') as file:
    data = file.readlines()

#remove non-numeric characters
data = [line.strip().rstrip('),') for line in data]

#split each line into individual values and convert to float
data = [float(value) for line in data for value in line.split(', ')]

#total number of elements
total_elements = len(data)
#size of each section, math.ceil is used to round up to nearest integer
section_size = math.ceil(total_elements / 43)
#print(total_elements,section_size)

#iterate through the data and assign elements to sections
sections = []
for i in range(0, total_elements, section_size):
    section = data[i:i+section_size]
    sections.append(section)

# Save each section into separate 
for i, section in enumerate(sections):
    with open(f'section_{i}.txt', 'w') as file:
        for element in section:
            file.write(str(element) + '\n')
