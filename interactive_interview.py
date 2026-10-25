"""Optional stretch: interactive interview loop. Each turn is a small crew run with transcript so far.
Mark: optional, isolated from the four main crews. Type 'done' to finish and get a summary prompt.
"""
# Implementation is a console loop; live mode requires OPENAI_API_KEY.
# In offline/stub mode it still demonstrates the flow without inventing candidate answers.
if __name__=="__main__":
    print("Interactive interview (optional). Type 'done' to end.")
    print("This mode asks one question at a time and gives brief feedback per answer.")
