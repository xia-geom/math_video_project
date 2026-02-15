# 1. Create the first set
# We use 'frozenset' so it can be placed inside another set
set_A = frozenset({1, 2})

# 2. Create another set that contains set_A as an element
set_B = {set_A, 3, 4}

print(f"Set A: {set_A}")
print(f"Set B: {set_B}")
print("-" * 20)

# 3. Check if Set A is IN Set B (Membership)
# Mathematical notation: A ∈ B

# inA = 1 in set_A
# print(f"Is 1 an element of A? {inA}")

# inB = 1 in set_B
# print(f"Is 1 an element of B? {inB}")

# is_element = set_A in set_B
# print(f"Is A an element of B? {is_element}") 


# 4. Check if Set A is INCLUDED in Set B (Subset)
# Mathematical notation: A ⊆ B
# This checks if 1 and 2 are individually inside Set B
# is_subset = set_A.issubset(set_B)
# print(f"Is A a subset of B?   {is_subset}")