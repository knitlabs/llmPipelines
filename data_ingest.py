from typing import Literal
from bs4 import BeautifulSoup
from bs4.element import Comment,NavigableString
from urllib.request import Request, urlopen
from pypdf import PdfReader
from openai import OpenAI
from tqdm import tqdm
import base64
import warnings

openai_client = openai.OpenAI(api_key=openai_key)
openai_text_image_model = 'gpt-4o'
openai_audio_model = 'whisper-1'

_INPUTS = Literal["text","url","audio","pdf","graph","image","word"]


client = OpenAI(api_key=openai_key)

def tag_visible(element):
    '''
    Function to identify visible text elements from a given webpage.
    These are text data part of the following parent tags.

    'style', 'script', 'head', 'title', 'meta', '[document]','i'

    Comments and Navigable Strings are also excluded. So are headings belonging to elements in 'dropdown-title' class
    '''
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]','i']:
        return False
    if 'class' in element.attrs:
        if "dropdown-title" in element.attrs['class']:
            return False
        if "btn" in element.attrs["class"]:
            return False
        if "nav__title" in element.attrs["class"]:
            return False
            return False
    if isinstance(element, Comment):
        return False
    if isinstance(element,NavigableString):
        return False
    return True


def text_from_html(body):
    '''
    Extracting text from webpage
    '''
    soup = BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


def encode_image(image_path):
  '''
  Opens a image in a given path and returns it's base64 encoded string
  '''
  with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def graph_to_json(image_base64):
  '''
  Convert data with a base64 encoded image in a graph to json.
  '''

  graph_prompt = "Convert the graphs into a structured JSON. Only return the JSON"
  response = client.chat.completions.create(
      model=openai_text_image_model,
      messages=[
          {
              "role": "user",
              "content": [
                  {
                      "type": "text",
                      "text": graph_prompt,
                  },
                  {
                      "type": "image_url",
                      "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                  },
              ],
          }
      ],
  )

  try:
    #Extracting the JSON via regex
    return json.loads(re.findall("```json([^`]{3,})",response.choices[0].message.content)[0])

  except:
    return response.choices[0].message.content

def fetch_graph_image(path:str) -> dict:
  '''
  Convert images of graphs to it's original JSON. Uses GPT to convert graph back into json. It takes just the image path as the input.
  And returns a suitable JSON.

  '''
  image = encode_image(path)
  return graph_to_json(image)

def describe_image(image_base64:str) -> str:
  '''
  Describe the image in detail and converts it into a string. The function takes the base64 encoded image. Suitable for non-graphical images and when descriptive text is necessary than a structured output.
  '''
  image_prompt = "You are tasked with writing elaborate description of the given image. An artist should be able to recreate the image based on the description. Write only the description."

  response = client.chat.completions.create(
      model=openai_text_image_model,
      messages=[
          {
              "role": "user",
              "content": [
                  {
                      "type": "text",
                      "text": image_prompt,
                  },
                  {
                      "type": "image_url",
                      "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                  },
              ],
          }
      ],
  )

  try:
    return response.choices[0].message.content
  except:
    raise Exception("Something went wrong with the image")


def fetch_image(path:str) -> str:
  '''
  Takes a image path as input and returns a detailed description of the image. The output is a string.
  '''
  image_encoded = encode_image(path)
  return describe_image(image_encoded)


def fetch_pdf(path:str,support_image:bool=True,graph_mode:bool=True) -> str:
    '''Function that takes in a PDF file as returns content present in it.

       It takes three arguments:
       - path: Path of the pdf
       - support_image: Does the images in the pdf needs to be incorporated into the text data.(Uses a GPT model to extract information)
       - graph_mode: The image contents are converted into JSON strings and are appenended into the document string. Ideal when document contains graphs, and flow diagrams.


       Returns a string containing the contents of the pdf


       '''
    reader = PdfReader(path)
    content = ""
    number_of_pages = len(reader.pages)
    for pg in range(number_of_pages):
        content = content + reader.pages[pg].extract_text()
        content = content + "\n\n"
        image_files = reader.pages[pg].images
        pdf_name = path.split("/")[-1]
        if len(image_files) > 0 and support_image:
            if pg == 0:
                continue
            else:
                try:
                    for image_file_object in image_files:
                      image_data = base64.b64encode(image_file_object.data).decode("utf-8")
                      if graph_mode:
                        image_data_dict = graph_to_json(image_data)
                        content = content +"\n Data Visualised: " + str(image_data_dict) + "\n\n"
                      else:
                        image_data_dict = describe_image(image_data)
                        content = content +"\n Image Description: " + str(image_data_dict) + "\n\n"
                except:
                    continue
    return content




def fetch_url(url:str) -> str:
    '''
    Function to extract text content from a given website. Takes the url as an input.

    It uses Mozilla User Agent to access webpages and returns texts that are part of 'h1', 'h2', 'h3', 'h4', 'h5', 'h6','p' tags.
    Filters out unwanted html content.
    '''
    try:
        req = Request(url,headers={'User-Agent':"Mozilla/5.0"})
        html = urlopen(req)
        soup = BeautifulSoup(html,'html.parser')
        text = soup.findAll(['h1', 'h2', 'h3', 'h4', 'h5', 'h6','p'])
        visible_texts = filter(tag_visible, text)
        return "\n".join([txt.text for txt in visible_texts])
    except:
        raise Exception("Something went wrong with the URL")



def fetch_audio(path:str) -> str:
  '''
  Function that takes in an path to an audio file and converts it into transcripts. It takes two variables.
    - path : The path to the audio file.

    The function automatically translates non-english speech to english. However the language support is limited.
    Additionally, the audio size is limited to 25MB as of now
  '''

  with open(path,"rb") as audio_file:

    transcript = client.audio.translations.create(
    model=openai_audio_model,
    file=audio_file
  )

  return transcript.text

def fetch_word(path:str,support_image:bool=True,graph_mode:bool=True) -> str:
  '''
  Converts a word document into text
       It takes three arguments:
       - path: Path of the pdf
       - support_image: Does the images in the pdf needs to be incorporated into the text data.(Uses a GPT model to extract information)
       - graph_mode: The image contents are converted into JSON strings and are appenended into the document string. Ideal when document contains graphs, and flow diagrams.
       Returns a string containing the contents of the word
  '''

  doc = Document(path)
  content = ""
  for para in doc.paragraphs:
      content += para.text + "\n\n"

  if support_image:
    image_counter = 0
    for rel in doc.part.rels.values():
      if "image" in rel.target_ref:
        image_part = rel.target_part.blob
        image_data = base64.b64encode(image_part).decode("utf-8")
        if graph_mode:
          content +="Graph Visualised :" + str(image_counter) + " : " + str(graph_to_json(image_data)) + "\n\n"
        else:
          content += "Image Description :" + str(image_counter) + " : " + describe_image(image_data) + "\n\n"
        image_counter += 1
  return content



def fetch_input(content:str,type: _INPUTS= "text",input_images_pdf:bool=True,graph_mode:bool=True) -> str:
    '''
    Returns text from a given input. The input could be either text or url.
    If URL the text contents from the website is fetched. Text is passed as is.

    Example Usage:
    >>> fetch_input("Hello World")
    ['Hello World']

    >>> fetch_input("Hello World", "text")
    ['Hello World']

    >>> fetch_input("https://www.lipsum.com/", "url")
    ['Lorem Ipsum\n"Neque porro quisquam est qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit..."\n"There is no one who loves pain itself, who seeks after it and wants to have it, simply because it is pain..."\nWhat is Lorem Ipsum?\nLorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry\'s standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.\nWhy do we use it?\nIt is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. The point of using Lorem Ipsum is that it has a more-or-less normal distribution of letters, as opposed to using \'Content here, content here\', making it look like readable English. Many desktop publishing packages and web page editors now use Lorem Ipsum as their default model text, and a search for \'lorem ipsum\' will uncover many web sites still in their infancy. Various versions have evolved over the years, sometimes by accident, sometimes on purpose (injected humour and the like).\nWhere does it come from?\nContrary to popular belief, Lorem Ipsum is not simply random text. It has roots in a piece of classical Latin literature from 45 BC, making it over 2000 years old. Richard McClintock, a Latin professor at Hampden-Sydney College in Virginia, looked up one of the more obscure Latin words, consectetur, from a Lorem Ipsum passage, and going through the cites of the word in classical literature, discovered the undoubtable source. Lorem Ipsum comes from sections 1.10.32 and 1.10.33 of "de Finibus Bonorum et Malorum" (The Extremes of Good and Evil) by Cicero, written in 45 BC. This book is a treatise on the theory of ethics, very popular during the Renaissance. The first line of Lorem Ipsum, "Lorem ipsum dolor sit amet..", comes from a line in section 1.10.32.\nThe standard chunk of Lorem Ipsum used since the 1500s is reproduced below for those interested. Sections 1.10.32 and 1.10.33 from "de Finibus Bonorum et Malorum" by Cicero are also reproduced in their exact original form, accompanied by English versions from the 1914 translation by H. Rackham.\nWhere can I get some?\nThere are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words which don\'t look even slightly believable. If you are going to use a passage of Lorem Ipsum, you need to be sure there isn\'t anything embarrassing hidden in the middle of text. All the Lorem Ipsum generators on the Internet tend to repeat predefined chunks as necessary, making this the first true generator on the Internet. It uses a dictionary of over 200 Latin words, combined with a handful of model sentence structures, to generate Lorem Ipsum which looks reasonable. The generated Lorem Ipsum is therefore always free from repetition, injected humour, or non-characteristic words etc.\nThe standard Lorem Ipsum passage, used since the 1500s\n"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."\nSection 1.10.32 of "de Finibus Bonorum et Malorum", written by Cicero in 45 BC\n"Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?"\n1914 translation by H. Rackham\n"But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure, but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure. To take a trivial example, which of us ever undertakes laborious physical exercise, except to obtain some advantage from it? But who has any right to find fault with a man who chooses to enjoy a pleasure that has no annoying consequences, or one who avoids a pain that produces no resultant pleasure?"\nSection 1.10.33 of "de Finibus Bonorum et Malorum", written by Cicero in 45 BC\n"At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non recusandae. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat."\n1914 translation by H. Rackham\n"On the other hand, we denounce with righteous indignation and dislike men who are so beguiled and demoralized by the charms of pleasure of the moment, so blinded by desire, that they cannot foresee the pain and trouble that are bound to ensue; and equal blame belongs to those who fail in their duty through weakness of will, which is the same as saying through shrinking from toil and pain. These cases are perfectly simple and easy to distinguish. In a free hour, when our power of choice is untrammelled and when nothing prevents our being able to do what we like best, every pleasure is to be welcomed and every pain avoided. But in certain circumstances and owing to the claims of duty or the obligations of business it will frequently occur that pleasures have to be repudiated and annoyances accepted. The wise man therefore always holds in these matters to this principle of selection: he rejects pleasures to secure other greater pleasures, or else he endures pains to avoid worse pains."']

    >>> fetch_input("/path/to/audio.mp3", "audio")
    ['Transcript of the audio in english']

    >>> fetch_input("path/to/document.pdf", "pdf")
    ['Content of the PDF']

    >>> fetch_input("path/to/graph.png", "graph_image")
    {'x_axis': [...], 'y_axis': [...], 'data': [...]}

    >>> fetch_input("path/to/image.jpg", "image")
    'Detailed description of the image...'
    '''
    if type.lower() not in _INPUTS.__args__:
        raise ValueError("Unsupported input")
    else:
        try:
            if type == "text":
                return content.split("\n\n")
            if type == "url":
                return fetch_url(content).split("\n\n")
            if type == "audio":
                return fetch_audio(content).split("\n\n")
            if type == "pdf":
                return fetch_pdf(content,support_image=input_images_pdf).split("\n\n")
            if type =="graph":
              return fetch_graph_image(content)
            if type == "image":
              return fetch_image(content)
        except:
            warnings.warn("Something went wrong, ignoring current file")

