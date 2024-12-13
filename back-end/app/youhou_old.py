import fitz  # PyMuPDF
import spacy
import re
import os
from faker import Faker

def anon(file):

    fake = Faker()


    print("youhou")

    print(os.getcwd())

    HOME = os.getcwd()

    # Load the French spaCy language model
    nlp = spacy.load('fr_core_news_md')

    # Open the PDF file
    doc = fitz.open(file)

    # Function to extract entities (e.g., names, dates, addresses, emails, IBAN, etc.)
    def redact_entities(page, text):
        # Process the extracted text with spaCy
        doc = nlp(text)
        
        # Store bounding boxes for redacting
        redaction_rects = []

        # Loop through the named entities detected by spaCy
        for ent in doc.ents:
            # Check the entity type (can be PERSON, GPE for locations, DATE for dates, etc.)
            if ent.label_ in ["EVENT", "FAC", "GPE", "LANGUAGE", "LOCATION",
                            "MONEY", "NORP", "ORDINAL", "PERSON", 
                            "PRODUCT", "QUANTITY", "TIME", "WORK_OF_ART"]:
                print(f"Detected entity: {ent.text} ({ent.label_})")
                
                # Search for the entity's position in the PDF
                rects = page.search_for(ent.text)
                if rects:  # Check if search returned any results
                    for rect in rects:
                        redaction_rects.append(rect)
        
        # Regex patterns to detect various types of sensitive information
        
        # 1. Email Addresses (simple pattern, can be more complex for different cases)
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, text)
        for email in emails:
            print(f"Detected email: {email}")
            rects = page.search_for(email)
            if rects:  # Check if search returned any results
                for rect in rects:
                    redaction_rects.append(rect)
        
        # 2. IBAN (International Bank Account Number)
        iban_pattern = r'\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b'  # Simplified IBAN format
        ibans = re.findall(iban_pattern, text)
        for iban in ibans:
            print(f"Detected IBAN: {iban}")
            rects = page.search_for(iban)
            if rects:  # Check if search returned any results
                for rect in rects:
                    redaction_rects.append(rect)





        # Numéros commençant par 0 ou +33 et respectant le format standard
        phone_pattern = r'\b(?:(?:\+|00)33[\s.-]?(?:\(0\)[\s.-]?)?|0)[1-9](?:[\s.-]?\d{2}){4}\b'

            # Recherche des numéros de téléphone valides
        phone_numbers = re.findall(phone_pattern, text)

        # Supprimer chaque numéro valide détecté
        for phone in phone_numbers:
            print(f"Detected valid phone number: {phone}")
            rects = page.search_for(phone)
            if rects:  # Vérifie si des résultats ont été trouvés
                for rect in rects:
                    redaction_rects.append(rect)

        
        # 4. Dates in various formats (e.g., 12/12/2024, 2024-12-12, Dec 12, 2024, etc.)
        #date_pattern = r'(\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|[A-Za-z]{3,9} \d{1,2}, \d{4})'
        #dates = re.findall(date_pattern, text)
        #for date in dates:
            #print(f"Detected date: {date}")
            #rects = page.search_for(date)
            #if rects:  # Check if search returned any results
                #for rect in rects:
                    #redaction_rects.append(rect)

            # 5. First Names and Last Names (simple pattern, can be more complex for different cases)
        name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b'
        names = re.findall(name_pattern, text)
        for name in names:
            print(f"Detected name: {name}")
            rects = page.search_for(name)
            if rects:  # Check if search returned any results
                for rect in rects:
                    redaction_rects.append(rect)
        
        # Use regex to find addresses of the format "21, chemin Thierry De Sousa-sur-Mer 14044"
        address_pattern = r'\d{1,4},?\s(?:[A-Za-z0-9\-\,\s]+(?:[A-Za-z0-9\-\,]+)+)\s*\d{4,5}'
        addresses = re.findall(address_pattern, text)
        print(f"Addresses found: {addresses}")  # Debugging line to check found addresses
        for address in addresses:
            print(f"Detected address: {address}")
            rects = page.search_for(address)
            if rects:
                for rect in rects:
                    redaction_rects.append(rect)

        return redaction_rects

    # Loop through each page in the document
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Extract text from the page
        page_text = page.get_text("text")
        
        # Redact the entities detected on the page
        redaction_rects = redact_entities(page, page_text)
        
        # Add redactions for each detected entity
        for rect in redaction_rects:
            annot = page.add_redact_annot(rect)
        
        # Apply the redactions (removes the redacted content from the PDF)
        page.apply_redactions()
        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)

    # Save the modified PDF
    doc.save(f"files/{os.path.basename(file)}", garbage=3, deflate=True)