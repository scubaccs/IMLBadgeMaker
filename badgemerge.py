import os
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io

def add_name_to_pdf(template_path, name, output_folder="output"):
    """
    Add a name to a PDF template and save as a new file named after the person.
    Creates a duplex-ready PDF with the same content on both sides.
    
    Args:
        template_path: Path to the template PDF
        name: Name to add to the PDF
        output_folder: Folder to save the output PDFs
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Output filename based on the name
    output_path = os.path.join(output_folder, f"{name}.pdf")
    
    # Read the template PDF
    with open(template_path, "rb") as template_file:
        pdf_reader = PyPDF2.PdfReader(template_file)
        pdf_writer = PyPDF2.PdfWriter()
        
        # Process each page in the template
        for page_num in range(len(pdf_reader.pages)):
            # Get page dimensions
            page = pdf_reader.pages[page_num]
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)
            
            # Create a temporary canvas with reportlab
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=(page_width, page_height))
            
            # Register and use the font
            obviously_font_path = "./ObviouslyNarwSemi.ttf"  # Replace with actual path
            pdfmetrics.registerFont(TTFont("Obviously Narw Semi", obviously_font_path))
            can.setFont("Obviously Narw Semi", 17)
            
            # Add the name - position can be adjusted as needed
            text_width = can.stringWidth(name, "Obviously Narw Semi", 17)
            x_position = (page_width - text_width) / 2
            y_position = 44  # 2 inches from top (72 points per inch)
            
            can.drawString(x_position, y_position, name)
            can.save()
            
            # Move to the beginning of the StringIO buffer
            packet.seek(0)
            
            # Create a new PDF with the text
            overlay = PyPDF2.PdfReader(packet)
            
            # Merge the original page with the overlay
            page.merge_page(overlay.pages[0])
            
            # Add the merged page to the output PDF
            pdf_writer.add_page(page)
            
            # Add the same page again for duplex printing
            # We need to create a copy of the page, as PyPDF2 doesn't allow adding the same page object twice
            pdf_writer.add_page(page)
        
        # Write the output PDF
        with open(output_path, "wb") as output_file:
            pdf_writer.write(output_file)
            
    return output_path

def process_names_file(template_path, names_file_path, output_folder="output"):
    """
    Process a file containing names and create duplex PDFs for each name
    
    Args:
        template_path: Path to the template PDF
        names_file_path: Path to text file with names (one per line)
        output_folder: Folder to save the output PDFs
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Read the names from the text file
    with open(names_file_path, "r") as names_file:
        names = [name.strip() for name in names_file.readlines()]
    
    # Process each name
    for name in names:
        if name:  # Skip empty lines
            output_path = add_name_to_pdf(template_path, name, output_folder)
            print(f"Created duplex PDF: {output_path}")

if __name__ == "__main__":
    import argparse
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(
        description="Add names from a text file to a PDF template and create duplex PDFs."
    )
    parser.add_argument("template_pdf", help="Path to the template PDF file")
    parser.add_argument("names_file", help="Path to the text file containing names (one per line)")
    parser.add_argument(
        "--output", "-o", 
        default="output", 
        help="Output folder for the generated PDFs (default: 'output')"
    )
    
    args = parser.parse_args()
    
    # Process the files
    process_names_file(args.template_pdf, args.names_file, args.output)
    print(f"All duplex PDFs have been generated in the '{args.output}' folder.")