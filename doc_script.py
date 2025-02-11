import os
import re
import markdown
from PyPDF2 import PdfReader


project_folder = "ahmed"

def extract_year_and_title(pdf_path):
    """
    Extracts the publication year and title from a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        A tuple containing the year (as an integer) and the title (as a string), 
        or (None, None) if extraction fails.
    """
    try:
        with open(pdf_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            # Extract text from the first page (adjust as needed)
            page_text = pdf_reader.pages[0].extract_text()

            # Basic pattern to find year (adjust based on common formats)
            year_match = re.search(r'\b(20\d{2})\b', page_text) 
            if year_match:
                year = int(year_match.group(1))
            else:
                return None, None

            if pdf_reader.metadata and pdf_reader.metadata.title:
                title = pdf_reader.metadata.title
            else:

                # Basic pattern to find title (adjust based on common formats)
                title_match = re.search(r'^(.*?)\s*-', page_text, flags=re.MULTILINE) 
                if title_match:
                    title = title_match.group(1).strip()
                else:
                    return None, None

            return year, title

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return None, None

def rename_pdf_and_move_to_unread(pdf_path,unread_folder):
    year, title = extract_year_and_title(pdf_path)
    if year and title:
        new_filename = f"({year}){title}.pdf"
        new_dir = unread_folder
        new_path = os.path.join(new_dir, new_filename)

        # Create a copy of the original file with the new name
        try:
            os.replace(pdf_path, new_path) 
        except OSError as e: 
            # print(e)
            # If 'replace' fails (e.g., file already exists), use 'copy' and then delete
            import shutil
            print(f"Renaming {pdf_path} to {new_path}")
            shutil.copyfile(pdf_path, new_path)
            os.remove(pdf_path)

        print(f"Renamed {pdf_path} to {new_path}")

def create_or_update_markdown(read_folder, unread_folder):
    """
    Creates or updates a markdown file with a list of PDFs in 'read' and 'unread' folders.

    Args:
        read_folder: Path to the folder containing read PDFs.
        unread_folder: Path to the folder containing unread PDFs.
    """

    # Extract year from PDF filenames
    def extract_year(filename):
        match = re.search(r"(\d{4})", filename)
        return int(match.group(1)) if match else 0

    # Sort PDFs by year
    def sort_by_year(pdf_list):
        return sorted(pdf_list, key=lambda x: extract_year(x))

    # Get list of PDFs in each folder
    read_pdfs = sort_by_year(os.listdir(read_folder))
    unread_pdfs = sort_by_year(os.listdir(unread_folder))

    # Create markdown content
    markdown_content = f"# PDF Reading Status\n\n"
    markdown_content += f"**Read:**\n\n"
    markdown_content += "\n".join(f"- {pdf}" for pdf in read_pdfs) + "\n\n"
    markdown_content += f"**Unread:**\n\n"
    markdown_content += "\n".join(f"- {pdf}" for pdf in unread_pdfs) + "\n\n"

    # Update or create markdown file
    with open(os.path.join(project_folder,"docs","survey_status.md"), "w") as f:
        f.write(markdown_content)



# Example usage
folder_to_process = os.path.join(project_folder,"Survey_Papers","downloads") 
unread_folder = os.path.join(project_folder,"Survey_Papers","unread")
for filename in os.listdir(folder_to_process):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(folder_to_process, filename)
        rename_pdf_and_move_to_unread(pdf_path, unread_folder)

# Example usage
read_folder = os.path.join(project_folder,"Survey_Papers","read")

create_or_update_markdown(read_folder, unread_folder)