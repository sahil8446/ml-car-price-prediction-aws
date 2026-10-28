import streamlit as st

def square(x):
    return x * x

num = st.number_input("Enter a number:")

if st.button("calculate"):
    result = square(num)
    st.write(f"The square of {num} is {result}")
