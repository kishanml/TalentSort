import os
import re
import fitz
import shutil
from lxml import etree
from collections import Counter

class ResumeParser():

    def __init__(self) -> None:
        self.terminal_tags = ["li", "a", "img", "p", "h1", "h2", "h3", "h4", "h5", "h6", "br", "div", "span"]

    @staticmethod
    def extract_html_from_resume( file_path : str , save_path : str = "temp" ):

        if os.path.exists(save_path):
            shutil.rmtree(save_path)
        os.makedirs(save_path)
            
        html_filepaths = []

        filename = os.path.splitext(os.path.basename(file_path))[0]
        document = fitz.open(file_path)
        for i,page in enumerate(document):
            text = page.get_text("html")
            page_save_path = os.path.join(save_path,f"{filename}_page_{i+1}.html")
            with open(page_save_path, "w") as fp:
                fp.write(text)

            html_filepaths.append(page_save_path)

        document.close()
        
        return html_filepaths

    @staticmethod
    def get_parsed_dict( lxml_tree ):
        parsed_dict = {}
        for ele in lxml_tree.iter():
            path = lxml_tree.getpath(ele)
            tags = list(filter(lambda x: x not in ["","html","body"], path.split("/")))
            root = parsed_dict
            for tag in tags[:-1]:
                if len(tag):
                    root = root[tag]["next_node"]
            root[tags[-1]] = {
                "next_node": {},
                "code": etree.tostring(ele).decode(),
                "xpath": path
            }
        
        return parsed_dict
        
    @staticmethod
    def get_texts_in_between(l1, l2, start=0):
        step = len(l2)
        if step == 0:
            return start, start
        for i in range(start, len(l1) - step + 1, step):
            if l2 == l1[i: i + step]:
                return i, i + step
        return start, start
    
    def traverse_tree(self,key, value, lxml_tree, result, prefix="", level=0 ):
        
        if not value["next_node"]:
            if key in self.terminal_tags:
                if key == "a":
                    attrs = lxml_tree.xpath(value["xpath"])[0].attrib
                    text = "".join(list(lxml_tree.xpath(value["xpath"])[0].itertext()))
                    
                    if "href" in attrs.keys() and text is not None:
                        res = text + "( " + "### Link: " + lxml_tree.xpath(value["xpath"])[0].attrib["href"] + " )."
                    elif "href" in attrs.keys() :
                        res = "( " + "### Link: " + lxml_tree.xpath(value["xpath"])[0].attrib["href"] + " )."
                    elif text is not None:
                        res = text
                    else:
                        res = ""
                elif key == "img":
                    attrs = lxml_tree.xpath(value["xpath"])[0].attrib
                    if "src" in attrs.keys():
                        res = "( ### Image: " + lxml_tree.xpath(value["xpath"])[0].attrib["src"] + " )."
                    else:
                        res = ""
                elif key == "li":
                    text = "".join(list(lxml_tree.xpath(value["xpath"])[0].itertext()))
                    if text is not None:
                        res = "> " + text
                    else:
                        res = ""
                elif key == "br":
                    res = "\n"
                else:
                    text = "".join(list(lxml_tree.xpath(value["xpath"])[0].itertext()))
                    if text is not None:
                        res = text
                    else:
                        res = ""
                result.append({
                    "text": res if res is not None else "",
                    "level": level
                })
                return res if res is not None else ""
            else:
                result.append({
                    "text": "",
                    "level": level
                })
                return ""
            
        else:
            full_text = ""
            start = 0
            try:
                main_element = lxml_tree.xpath(value["xpath"])[0]
                main_texts = list(main_element.itertext())
                for next_node_key, next_node_value in value["next_node"].items():
                    try:
                        cur_element = lxml_tree.xpath(next_node_value["xpath"])[0]
                        texts = list(cur_element.itertext())
                    except:
                        texts = []
                    idx1, idx2 = ResumeParser.get_texts_in_between(main_texts, texts, start)
                    if key == "a":
                        attrs = lxml_tree.xpath(value["xpath"])[0].attrib
                        if "href" in attrs.keys() :
                            res = prefix + self.traverse_tree(next_node_key, next_node_value, lxml_tree, result, prefix,
                                                              level + 1) + "( " + "### Link:" + \
                                  lxml_tree.xpath(value["xpath"])[0].attrib["href"] + " )."
                            result[-1]["text"] = prefix + result[-1]["text"] + "( " + "### Link:" + \
                                                 lxml_tree.xpath(value["xpath"])[0].attrib["href"] + " )."
                        else:
                            res = prefix + self.traverse_tree(next_node_key, next_node_value, lxml_tree, result, prefix,
                                                              level + 1)
                            result[-1]["text"] = prefix + result[-1]["text"]
                    elif key == "ol" or key == "ul":
                        res = prefix + " " + self.traverse_tree(next_node_key, next_node_value, lxml_tree, result,
                                                                prefix + " ", level + 1)
                        result[-1]["text"] = prefix + " " + result[-1]["text"]
                    elif key == "li":
                        res = prefix + "> " + self.traverse_tree(next_node_key, next_node_value, lxml_tree, result,
                                                                 prefix + "> ", level + 1)
                        result[-1]["text"] = prefix + "> " + result[-1]["text"]
        
                    elif key == "div":
                        res = prefix + "\n" + self.traverse_tree(next_node_key, next_node_value, lxml_tree, result,
                                                                 prefix, level + 1)
                        result[-1]["text"] = prefix + "\n" + result[-1]["text"]
                    else:
                        res = prefix + self.traverse_tree(next_node_key, next_node_value, lxml_tree, result, prefix,
                                                          level + 1)
                        
                        result[-1]["text"] = prefix + result[-1]["text"]
                    full_text += prefix + "".join(main_texts[start: idx1]) + res[len(prefix):]
                    
                    result[-1]["text"] = result[-1]["text"][len(prefix):]
                    result.insert(-1, {
                        "text": prefix + "".join(main_texts[start: idx1]),
                        "level": level
                    })
                    start = idx2
            except Exception as e:
                print(e)
                pass
            finally:
                return full_text

    @staticmethod
    def postprocess_text(text):
        
        def escape_specific(text, chars_to_escape):
            escaped_text = text
            for char in chars_to_escape:
                escaped_text = escaped_text.replace(char, "\\" + char)
            return escaped_text
        
        chars_to_escape = "()+"
        split_text = re.split(r'\n+', text)
        repeated_texts = [ k for k,v in Counter(split_text).items() if v>1]
        
        for txt in repeated_texts:

            escaped_string = escape_specific(txt, chars_to_escape)
            match = re.search(r"(?:\\n)*"+escaped_string, text)
            if match:
                start_index = match.start()
                end_index = match.end()
                text = text[:start_index] + text[end_index:]

        return text        
        
    @staticmethod
    def extract_text_from_resume( file_path : str ):

        full_text = ""
        document = fitz.open(file_path)
        for i,page in enumerate(document):
            text = page.get_text()
            full_text+=text+'\m'
        return full_text    
            
    def get_parsed_text_from_html(self, html_file_path : str ):
        
        html_tree = etree.parse(html_file_path)
        parsed_dict = ResumeParser.get_parsed_dict(html_tree)

        result = []
        extracted_text = self.traverse_tree("div", parsed_dict['div'], html_tree, result)

        return ResumeParser.postprocess_text(extracted_text)
        
        

        
if __name__ == "__main__":
    resume_text = ResumeParser.extract_text_from_resume("../resumes/applicationForm_16217910.pdf")
    print(resume_text)