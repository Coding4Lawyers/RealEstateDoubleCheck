import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
# import pypdftk
# import tempfile
# from PIL import Image
from pdf2image import convert_from_bytes
import pytesseract
import re

client = OpenAI(api_key=st.secrets["openai_apikey"])

# def flatten_pdf(uploaded_file):
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#             tmp_file.write(uploaded_file.read())
#             temp_file_path = tmp_file.name
#         #Save the uploaded file to a temporary location
        
#         #Fill the form using the temporary file path
#     flattened_pdf = pypdftk.fill_form(temp_file_path, out_file='flattened2.pdf', flatten=True)

#     print("flattened_pdf", flattened_pdf)

def checkChatGPT(text):
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    messages=[
        {"role": "system", "content": "You are an expert in real estate law and reading real estate contracts."},
        {"role": "user", "content": "How many days must the inspection take place after the inspection date? It should be around text like 'The obligation of Buyer to purchase the Property is contingent upon Buyer’s approval of inspections and review of all matters described'. Respond with the number only." + text}
    ]
    )

    print(completion)
    numbers = re.findall(r'\d+', completion.choices[0].message.content)[0]
    
    
    
    return numbers
def main():
    st.title("Real Estate Double Check")
    st.write("Upload a PDF file to perform real estate double check.")

    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    if uploaded_file is not None:
        # Perform real estate double check on the uploaded PDF
        # Convert each page of the PDF into an image
        page_images = convert_from_bytes(uploaded_file.read(), 300)  # 300 is the resolution in DPI

        full_text = ""
        for page in page_images:
            # Use Tesseract to extract text
            text = pytesseract.image_to_string(page)

            # Print the extracted text
            full_text += text
            print(text)
            # st.write(text)
            # output_filename = f"page_{page_number + 1}.png"
            # page.save(output_filename, "PNG")

        results = checkChatGPT(full_text)
        print("Results",results)
        if results != 15:
            st.error("Double check failed! Inspection time is typically 15 days however here it is " + results + " days.")
        else:
            st.success("Double Check Passed")

        # full_text = ""
        # reader = PdfReader(flattened_pdf)
        # for page in reader.pages:
        #     text = page.extract_text()
        #     full_text += text
        # st.success("Double check completed!")
        # st.write(full_text)

if __name__ == "__main__":
    main()