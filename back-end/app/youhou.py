import fitz  # PyMuPDF
import spacy
import re
import os
from faker import Faker

def anon(file):

    fake = Faker('fr_FR')  # Use French Faker to generate more realistic French data

    print("youhou")
    print(os.getcwd())

    HOME = os.getcwd()

    # Load the French spaCy language model
    nlp = spacy.load('fr_core_news_md')

    # Open the PDF file
    doc = fitz.open(file)

    def redact_and_replace_entities(page, text):
        # Process the extracted text with spaCy
        doc = nlp(text)
        
        # Store bounding boxes for annotating
        annotations = []

        # Loop through the named entities detected by spaCy
        for ent in doc.ents:
            # Check the entity type 
            if ent.label_ in ["EVENT", "FAC", "GPE", "LANGUAGE", "LOCATION",
                            "MONEY", "NORP", "ORDINAL", "PERSON", 
                            "PRODUCT", "QUANTITY", "TIME", "WORK_OF_ART"]:
                print(f"Detected entity: {ent.text} ({ent.label_})")
                
                # Generate replacement based on entity type
                if ent.label_ == "PERSON":
                    replacement = fake.name()
                elif ent.label_ in ["GPE", "LOCATION"]:
                    replacement = fake.city()
                elif ent.label_ == "MONEY":
                    replacement = f"{fake.random_number(digits=3)},00 €"
                else:
                    replacement = fake.word()
                
                # Search for the entity's position in the PDF
                rects = page.search_for(ent.text)
                if rects:
                    for rect in rects:
                        annotations.append({
                            'rect': rect, 
                            'original': ent.text, 
                            'replacement': replacement
                        })
        
        # 1. Email Addresses
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        for email in emails:
            print(f"Detected email: {email}")
            replacement = fake.email()
            rects = page.search_for(email)
            if rects:
                for rect in rects:
                    annotations.append({
                        'rect': rect, 
                        'original': email, 
                        'replacement': replacement
                    })
        
        # 2. IBAN 
        iban_pattern = r'\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b'
        ibans = re.findall(iban_pattern, text)
        for iban in ibans:
            print(f"Detected IBAN: {iban}")
            replacement = f"FR{fake.random_number(digits=2)} {fake.random_number(digits=5)} {fake.random_number(digits=5)} {fake.random_number(digits=11)} {fake.random_number(digits=2)}"
            rects = page.search_for(iban)
            if rects:
                for rect in rects:
                    annotations.append({
                        'rect': rect, 
                        'original': iban, 
                        'replacement': replacement
                    })

        # 3. Phone Numbers
        phone_pattern = (
            r'\b'
            r'(?:(?:\+|00)33[\s.-]?(?:\(0\)[\s.-]?)?|0)'
            r'[1-9](?:[\s.-]?\d{2}){4}'
            r'\b'
        )
        phone_numbers = re.findall(phone_pattern, text)
        for phone in phone_numbers:
            print(f"Detected phone number: {phone}")
            replacement = fake.phone_number()
            rects = page.search_for(phone)
            if rects:
                for rect in rects:
                    annotations.append({
                        'rect': rect, 
                        'original': phone, 
                        'replacement': replacement
                    })

        # 5. Names
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        names = re.findall(name_pattern, text)
        for name in names:
            print(f"Detected name: {name}")
            replacement = fake.name()
            rects = page.search_for(name)
            if rects:
                for rect in rects:
                    annotations.append({
                        'rect': rect, 
                        'original': name, 
                        'replacement': replacement
                    })
        
        # Addresses
        address_pattern = r'\d{1,4},?\s(?:[A-Za-z0-9\-\,\s]+(?:[A-Za-z0-9\-\,]+)+)\s*\d{4,5}'
        addresses = re.findall(address_pattern, text)
        for address in addresses:
            print(f"Detected address: {address}")
            replacement = f"{fake.building_number()}, {fake.street_name()} {fake.postcode()}"
            rects = page.search_for(address)
            if rects:
                for rect in rects:
                    annotations.append({
                        'rect': rect, 
                        'original': address, 
                        'replacement': replacement
                    })

        return annotations

    # Create a new PDF to write redacted content
    output_doc = fitz.open()

    # Loop through each page in the document
    for page_num in range(len(doc)):
        # Load the original page
        page = doc.load_page(page_num)
        
        # Create a new page in the output document
        new_page = output_doc.new_page(width=page.rect.width, height=page.rect.height)
        
        # Extract text from the page
        page_text = page.get_text("text")
        
        # Get annotations to replace
        annotations = redact_and_replace_entities(page, page_text)
        
        # Copy the original page content to the new page
        new_page.show_pdf_page(page.rect, doc, page_num)
        
        # Apply redactions to remove original content
        for annotation in annotations:
            rect = annotation['rect']
            new_page.add_redact_annot(rect)
        new_page.apply_redactions()

        # Add the replacement text
        for annotation in annotations:
            text_rect = annotation['rect']
            try:
                # Calculate the center of the rectangle
                center_x = text_rect.x0
                center_y = text_rect.y1
                
                # Create a font object
                font = fitz.Font()
                
                # Calculate the width of the replacement text
                text_width = font.text_length(annotation['replacement'], fontsize=min(text_rect.height * 1, 14))
                
                # Adjust the x position to center the text
                text_x = center_x - (text_width / 2)
                
                # Adjust the y position to center the text
                text_y = center_y - (text_rect.height / 2)
                
                # Insert the replacement text
                new_page.insert_text(
                    (center_x, center_y),  # Adjusted position to center the text
                    annotation['replacement'], 
                    color=(0, 0, 0),  # Black text
                    fontsize=min(text_rect.height * 1, 14)  # Adjust font size to fit, with a maximum size
                )
            except Exception as e:
                print(f"Error inserting text for {annotation['original']}: {e}")

    # Save the modified PDF
    output_doc.save(f"files/{os.path.basename(file)}")
    output_doc.close()
    doc.close()

    print("PDF redaction and replacement complete!")