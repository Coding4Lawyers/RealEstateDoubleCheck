import streamlit as st
from openai import OpenAI
# from dotenv import load_dotenv
import os
# import pypdftk
# import tempfile
# from PIL import Image
from pdf2image import convert_from_bytes
import pytesseract
import re
import json


# def flatten_pdf(uploaded_file):
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#             tmp_file.write(uploaded_file.read())
#             temp_file_path = tmp_file.name
#         #Save the uploaded file to a temporary location
        
#         #Fill the form using the temporary file path
#     flattened_pdf = pypdftk.fill_form(temp_file_path, out_file='flattened2.pdf', flatten=True)

#     print("flattened_pdf", flattened_pdf)

def checkChatGPT(text,gpt_version):

    client = OpenAI(api_key=st.secrets["openai_apikey"])
    answer_data = '''{
        "How many days must the inspection take place after the inspection date? Found under section 'General Inspection of Property Contingency'":"",
        "How many days is the seller's obligation to disclose the property condition? Found under section 'Seller's Obligation to Disclose'":"",
        "How many days does the buyer have to review the preliminary title report? Found under section 'Buyer's Review of Preliminary Title Report'":"",

    }'''

    completion = client.chat.completions.create(
    model=gpt_version,
    messages=[
        {"role": "system", "content": "You are an expert in real estate law and reading real estate contracts."},
        {"role": "user", "content": f"Please fill out the json object where the keys are what I want answered. {answer_data}. Only answer with the specific number of days requested. If there is no answer for a particular question, because the section is blank, respond with 'blank'.The text of the realestate document is as follows." + text}
    ]
    )

    print(completion)
    content = completion.choices[0].message.content
    print(content)
    json_string = content.replace('```json\n', '').replace('\n```', '').strip()

    # Parse the JSON string to convert it into an actual Python dictionary
    contract_info = json.loads(json_string)
    # numbers = re.findall(r'\d+', completion.choices[0].message.content)[0]
    
    
    
    return contract_info
def main():
    st.title("Real Estate Double Check")
    st.write("Upload a PDF file to perform real estate double check.")
    gpt_version = st.radio("Which ChatGPT do you want to use?", ("gpt-3.5-turbo-0125", "gpt-4o"))
    if gpt_version not in ["gpt-3.5-turbo-0125", "gpt-4o"]:
        st.error("Invalid ChatGPT version selected. Please choose a valid option.")
        return


    uploaded_file = st.file_uploader("Upload PDF", type="pdf")

    if uploaded_file is not None:
        # Perform real estate double check on the uploaded PDF
        # Convert each page of the PDF into an image
        page_images = convert_from_bytes(uploaded_file.read(), 300)  # 300 is the resolution in DPI

        full_text = ""
        for x,page in enumerate(page_images):
            # Use Tesseract to extract text
            text = pytesseract.image_to_string(page)
            st.write("OCRing page", x+1, "of", len(page_images))
            # Print the extracted text
            full_text += text
            #print(text)
            # st.write(text)
            # output_filename = f"page_{page_number + 1}.png"
            # page.save(output_filename, "PNG")

        results = checkChatGPT(full_text,gpt_version)
        st.subheader("Results From Chat GPT:")
        st.write(results)
        correct_answers = {
            "How many days must the inspection take place after the inspection date? Found under section 'General Inspection of Property Contingency'": "15",
            "How many days is the seller's obligation to disclose the property condition? Found under section 'Seller's Obligation to Disclose'": "10",
            "How many days does the buyer have to review the preliminary title report? Found under section 'Buyer's Review of Preliminary Title Report'":[10,15]
        }
        display = {
            "How many days must the inspection take place after the inspection date? Found under section 'General Inspection of Property Contingency'": "Inspection Date",
            "How many days is the seller's obligation to disclose the property condition? Found under section 'Seller's Obligation to Disclose'": "Seller Disclsoure Date",
            "How many days does the buyer have to review the preliminary title report? Found under section 'Buyer's Review of Preliminary Title Report'": "Preliminary Title Report Review"
        }
        for question, correct_answer in correct_answers.items():
            st.subheader(display[question] + ":")
            if(type(correct_answer) == list):
                #Range answer
                if(results[question] == 'blank'):
                    st.warning(f"{display[question]} is blank. Please check the contract for the typical number of days required. Average is between {correct_answer[0]} and {correct_answer[1]} days.")
                else:
                    number_only_answer = re.findall(r'\d+', results[question])[0]
                    if int(number_only_answer) >= correct_answer[0] and int(number_only_answer) <= correct_answer[1]:
                        st.success(f"{display[question]} is the typical number of days required.(Between {correct_answer[0]} and {correct_answer[1]} days)")
                    else:
                        st.error(f"{display[question]} is not the typical number of days required. Contract says {number_only_answer} days. Average is between {correct_answer[0]} and {correct_answer[1]} days.")
            else:
                #Single answer
                if(results[question] == 'blank'):
                    st.warning(f"{display[question]} is blank. Please check the contract for the typical number of days required. Average is between {correct_answer[0]} and {correct_answer[1]} days.")
                else:
                    number_only_answer = re.findall(r'\d+', results[question])[0]
                    if int(number_only_answer) == correct_answer:
                        st.success(f"{display[question]} is the typical number of days required.({correct_answer} days)")
                    else:
                        st.error(f"{display[question]} is not the typical number of days required. Contract says {number_only_answer} days. Average is {correct_answer} days.")

        # print("Results",results)
        # if results != 15:
        #     st.error("Double check failed! Inspection time is typically 15 days however here it is " + results + " days.")
        # else:
        #     st.success("Double Check Passed")

        # full_text = ""
        # reader = PdfReader(flattened_pdf)
        # for page in reader.pages:
        #     text = page.extract_text()
        #     full_text += text
        # st.success("Double check completed!")
        # st.write(full_text)

if __name__ == "__main__":
    main()