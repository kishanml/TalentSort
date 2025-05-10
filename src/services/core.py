from .resume_parser import ResumeParser


def get_text_from_resume(pdf_path : str):

    html_paths = ResumeParser.extract_html_from_resume(pdf_path,save_path="temp")
    return "\n".join(ResumeParser().get_parsed_text_from_html(path) for path in html_paths)


